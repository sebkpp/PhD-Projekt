using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Packages.Mirror
{
    public class Mirror : MonoBehaviour
    {
        [Header("Main Settings")]
        public Vector3   projectionDirection = Vector3.forward;
        public LayerMask mLayerMask          = -1;
        public int       mTextureSize        = 1024;
        [Tooltip("Camera used for reflection. Leave empty to use Camera.main.")]
        [SerializeField] private Camera _targetCamera;

        [Header("Advanced Settings")]
        public float mClipPlaneOffset    = 0.001f;
        public float nearClipLimit       = 0.2f;
        public bool  mDisablePixelLights = true;
        public int   mFramesNeededToUpdate;
        [Range(1, 8)]
        public int antiAliasing = 4;

        [Header("Render Texture Format")]
        [Tooltip("Default = ARGB32 (safe). RGB111110Float = HDR. RGB565 = 16-bit.")]
        public RenderTextureFormat textureFormat = RenderTextureFormat.Default;

        // ── Shader property IDs ──────────────────────────────────────────────────

        private static readonly int PropLeft  = Shader.PropertyToID("_ReflectionTexLeft");
        private static readonly int PropRight = Shader.PropertyToID("_ReflectionTexRight");

        // ── Private state ────────────────────────────────────────────────────────

        // NOTE: _insideRendering is static — prevents recursive mirror-in-mirror rendering.
        // Side effect: only one Mirror instance renders per frame in multi-mirror scenes.
        // This project uses at most one mirror, so this is acceptable.
        private static bool _insideRendering;

        private Camera _portalCamera;
        private int    _frameCounter;

        private RenderTexture _rtLeft;
        private RenderTexture _rtRight;
        private int           _oldTextureSize;
        private int           _oldAntiAliasing;
        private RenderTextureFormat _oldTextureFormat;

        private Renderer   _renderer;
        private Material[] _materials;

        // ── Lifecycle ────────────────────────────────────────────────────────────

        private void Awake()
        {
            _renderer  = GetComponent<Renderer>();
            _materials = _renderer.sharedMaterials;
        }

        private void OnDisable()
        {
            if (_rtLeft)        { DestroyImmediate(_rtLeft);                    _rtLeft       = null; }
            if (_rtRight)       { DestroyImmediate(_rtRight);                   _rtRight      = null; }
            if (_portalCamera)  { DestroyImmediate(_portalCamera.gameObject);   _portalCamera = null; }
        }

        // LateUpdate: all camera transforms are finalised; SubmitRenderRequest is
        // safe here because we are outside the active URP render loop.
        private void LateUpdate()
        {
            if (!Application.isPlaying) return;
            var cam = _targetCamera != null ? _targetCamera : Camera.main;
            if (cam != null) RenderReflection(cam);
        }

        // ── Public API ───────────────────────────────────────────────────────────

        /// <summary>Call when materials on the renderer are swapped at runtime.</summary>
        public void RefreshMaterials() => _materials = _renderer.sharedMaterials;

        // ── Render entry point ───────────────────────────────────────────────────

        public void RenderReflection(Camera mainCam)
        {
            if (!_renderer.isVisible)                                        return;
            if (!enabled || !_renderer.sharedMaterial || !_renderer.enabled) return;
            if (_insideRendering)                                             return;

            if (_frameCounter > 0) { _frameCounter--; return; }

            _insideRendering = true;
            _frameCounter    = mFramesNeededToUpdate;

            try { RenderMirror(mainCam); }
            finally { _insideRendering = false; }
        }

        // ── Render ───────────────────────────────────────────────────────────────

        private void RenderMirror(Camera mainCam)
        {
            // Bug 2 fix: .normalized — TransformDirection respects object scale;
            // a non-unit normal breaks the reflection matrix formula I − 2nnᵀ.
            var pos    = transform.position;
            var normal = transform.TransformDirection(projectionDirection).normalized;

            // Bug 4 fix: d carries NO offset. The clip-plane offset is applied
            // only inside CameraSpacePlane where it belongs (oblique clip plane).
            var d     = -Vector3.Dot(normal, pos);
            var plane = new Vector4(normal.x, normal.y, normal.z, d);

            var reflectionMatrix = Matrix4x4.identity;
            CalculateReflectionMatrix(ref reflectionMatrix, plane);

            EnsureRenderTextures();
            EnsurePortalCamera();

            if (mainCam.stereoEnabled)
            {
                RenderEye(mainCam, reflectionMatrix, pos, normal,
                    Camera.StereoscopicEye.Left,  _rtLeft);
                RenderEye(mainCam, reflectionMatrix, pos, normal,
                    Camera.StereoscopicEye.Right, _rtRight);
                AssignTextures(_rtLeft, _rtRight);
            }
            else
            {
                RenderEyeMono(mainCam, reflectionMatrix, pos, normal);
                // Mono: write same texture to both shader slots so the shader works
                // unchanged (unity_StereoEyeIndex = 0 → lerp picks left = correct).
                AssignTextures(_rtLeft, _rtLeft);
            }
        }

        private void RenderEye(Camera mainCam, Matrix4x4 reflectionMatrix,
            Vector3 pos, Vector3 normal, Camera.StereoscopicEye eye, RenderTexture rt)
        {
            // Extract world-space eye pose from the stereo view matrix.
            // GetStereoViewMatrix returns world→camera; invert to get camera→world.
            // Column layout of camera→world: [right | up | backward | position]
            // backward = +Z in camera space = opposite of looking direction.
            var camToWorld = mainCam.GetStereoViewMatrix(eye).inverse;
            var eyePos     = (Vector3)camToWorld.GetColumn(3);
            var eyeFwd     = -(Vector3)camToWorld.GetColumn(2); // camera looks along −Z
            var eyeUp      =  (Vector3)camToWorld.GetColumn(1);
            var eyeRight   =  (Vector3)camToWorld.GetColumn(0);
            var srcProj    = mainCam.GetStereoProjectionMatrix(eye);

            ConfigureAndSubmit(mainCam, reflectionMatrix, pos, normal,
                eyePos, eyeFwd, eyeUp, eyeRight, srcProj, rt);
        }

        private void RenderEyeMono(Camera mainCam, Matrix4x4 reflectionMatrix,
            Vector3 pos, Vector3 normal)
        {
            var t = mainCam.transform;
            ConfigureAndSubmit(mainCam, reflectionMatrix, pos, normal,
                t.position, t.forward, t.up, t.right, mainCam.projectionMatrix, _rtLeft);
        }

        private void ConfigureAndSubmit(Camera mainCam, Matrix4x4 reflectionMatrix,
            Vector3 pos, Vector3 normal,
            Vector3 eyePos, Vector3 eyeFwd, Vector3 eyeUp, Vector3 eyeRight,
            Matrix4x4 srcProj, RenderTexture rt)
        {
            CopyCameraProperties(mainCam, _portalCamera);

            // Reflect eye pose over the mirror plane.
            var refPos   = reflectionMatrix.MultiplyPoint3x4(eyePos);
            var refFwd   = reflectionMatrix.MultiplyVector(eyeFwd);
            var refUp    = reflectionMatrix.MultiplyVector(eyeUp);
            var refRight = reflectionMatrix.MultiplyVector(eyeRight);

            // Bug 5 fix: LookRotation is undefined when forward ≈ up (e.g. floor mirror,
            // camera looking straight down). Fall back to refRight as the up hint.
            var upHint = Mathf.Abs(Vector3.Dot(refFwd.normalized, refUp.normalized)) > 0.99f
                ? refRight
                : refUp;

            // Set transform so URP uses it for frustum culling.
            _portalCamera.transform.SetPositionAndRotation(
                refPos, Quaternion.LookRotation(refFwd, upHint));

            // Build the view matrix explicitly — do NOT use ResetWorldToCameraMatrix().
            // Unity evaluates it lazily; BuildObliqueProjection would read stale data.
            // Formula: world→camera with camera looking along −Z.
            var viewMatrix = new Matrix4x4();
            viewMatrix.SetRow(0, new Vector4( refRight.x,  refRight.y,  refRight.z, -Vector3.Dot(refRight, refPos)));
            viewMatrix.SetRow(1, new Vector4( refUp.x,     refUp.y,     refUp.z,    -Vector3.Dot(refUp,    refPos)));
            viewMatrix.SetRow(2, new Vector4(-refFwd.x,   -refFwd.y,   -refFwd.z,   Vector3.Dot(refFwd,   refPos)));
            viewMatrix.SetRow(3, new Vector4(0, 0, 0, 1));

            _portalCamera.worldToCameraMatrix = viewMatrix;
            _portalCamera.projectionMatrix    = BuildObliqueProjection(srcProj, viewMatrix, pos, normal);
            _portalCamera.cullingMask         = mLayerMask.value;
            _portalCamera.targetTexture       = rt;

            var oldPixelLightCount = QualitySettings.pixelLightCount;
            if (mDisablePixelLights) QualitySettings.pixelLightCount = 0;

            // Bug 1 fix: GL.invertCulling and pixelLightCount both in try/finally.
            // A reflection matrix has det = −1 → winding order flips → front-faces
            // become back-faces. invertCulling compensates. Both global state mutations
            // are restored on exception so the render pipeline is never left corrupted.
            GL.invertCulling = true;
            try
            {
                var request = new UniversalRenderPipeline.SingleCameraRequest();
                if (RenderPipeline.SupportsRenderRequest(_portalCamera, request))
                    RenderPipeline.SubmitRenderRequest(_portalCamera, request);
            }
            finally
            {
                GL.invertCulling = false;
                if (mDisablePixelLights) QualitySettings.pixelLightCount = oldPixelLightCount;
            }
            _portalCamera.targetTexture = null;
        }

        // ── Camera management ────────────────────────────────────────────────────

        private void EnsurePortalCamera()
        {
            if (_portalCamera != null) return;

            var go = new GameObject($"Mirror Portal Camera {GetInstanceID()}",
                typeof(Camera), typeof(Skybox))
            {
                hideFlags = HideFlags.DontSave
            };
            _portalCamera         = go.GetComponent<Camera>();
            _portalCamera.enabled = false;
            _portalCamera.tag     = "PortalCam";
        }

        private void EnsureRenderTextures()
        {
            bool sizeChanged   = _oldTextureSize   != mTextureSize;
            bool aaChanged     = _oldAntiAliasing  != antiAliasing;
            bool formatChanged = _oldTextureFormat != textureFormat;

            if (_rtLeft != null && !sizeChanged && !aaChanged && !formatChanged) return;

            if (_rtLeft)  DestroyImmediate(_rtLeft);
            if (_rtRight) DestroyImmediate(_rtRight);
            _rtLeft           = CreateRT("Left");
            _rtRight          = CreateRT("Right");
            _oldTextureSize   = mTextureSize;
            _oldAntiAliasing  = antiAliasing;
            _oldTextureFormat = textureFormat;
        }

        private RenderTexture CreateRT(string label) =>
            new RenderTexture(mTextureSize, mTextureSize, 24)
            {
                name         = $"__MirrorReflection{label}{GetInstanceID()}",
                isPowerOfTwo = true,
                hideFlags    = HideFlags.DontSave,
                antiAliasing = antiAliasing,
                format       = textureFormat,
            };

        private void CopyCameraProperties(Camera src, Camera dest)
        {
            dest.clearFlags      = src.clearFlags;
            dest.backgroundColor = src.backgroundColor;

            if (src.clearFlags == CameraClearFlags.Skybox)
            {
                // Skybox fix: if the main camera has no Skybox component it uses
                // RenderSettings.skybox (the scene skybox). Fall back to that so
                // the mirror doesn't render a grey background.
                var srcSkyMat = src.GetComponent<Skybox>()?.material ?? RenderSettings.skybox;
                var dstSky    = dest.GetComponent<Skybox>();

                if (srcSkyMat != null)
                {
                    dstSky.enabled  = true;
                    dstSky.material = srcSkyMat;
                }
                else
                {
                    dstSky.enabled  = false;
                    dest.clearFlags = CameraClearFlags.SolidColor;
                }
            }

            dest.farClipPlane     = src.farClipPlane;
            // Clamp to nearClipLimit: prevents near-clip artifacts when the source
            // camera is positioned very close to the mirror surface.
            dest.nearClipPlane    = Mathf.Max(src.nearClipPlane, nearClipLimit);
            dest.orthographic     = src.orthographic;
            dest.fieldOfView      = src.fieldOfView;
            dest.aspect           = src.aspect;
            dest.orthographicSize = src.orthographicSize;
            dest.depth            = 2;
            dest.GetUniversalAdditionalCameraData().renderPostProcessing = true;
        }

        private void AssignTextures(RenderTexture left, RenderTexture right)
        {
            foreach (var mat in _materials)
            {
                if (mat == null) continue;
                if (left  != null && mat.HasProperty(PropLeft))  mat.SetTexture(PropLeft,  left);
                if (right != null && mat.HasProperty(PropRight)) mat.SetTexture(PropRight, right);
            }
        }

        // ── Matrix helpers ───────────────────────────────────────────────────────

        private Matrix4x4 BuildObliqueProjection(Matrix4x4 srcProj, Matrix4x4 viewMatrix,
            Vector3 pos, Vector3 normal)
        {
            // sideSign = −1: reflected camera is on the back side of the mirror plane.
            // The world normal transforms to a camera-space vector pointing AWAY from
            // the camera. Negating it ensures the clip plane faces the camera.
            var clipPlane = CameraSpacePlane(viewMatrix, pos, normal, -1f);
            MakeProjectionMatrixOblique(ref srcProj, clipPlane);
            return srcProj;
        }

        private Vector4 CameraSpacePlane(Matrix4x4 worldToCameraMatrix,
            Vector3 pos, Vector3 normal, float sideSign)
        {
            // Bug 4 fix: offset applied HERE only (not in the reflection matrix plane).
            var offsetPos = pos + normal * mClipPlaneOffset;
            var cpos      = worldToCameraMatrix.MultiplyPoint(offsetPos);
            var cnormal   = worldToCameraMatrix.MultiplyVector(normal).normalized * sideSign;
            return new Vector4(cnormal.x, cnormal.y, cnormal.z, -Vector3.Dot(cpos, cnormal));
        }

        private static void CalculateReflectionMatrix(ref Matrix4x4 reflectionMat, Vector4 plane)
        {
            reflectionMat.m00 =  1f - 2f * plane[0] * plane[0];
            reflectionMat.m01 =      -2f * plane[0] * plane[1];
            reflectionMat.m02 =      -2f * plane[0] * plane[2];
            reflectionMat.m03 =      -2f * plane[3] * plane[0];
            reflectionMat.m10 =      -2f * plane[1] * plane[0];
            reflectionMat.m11 =  1f - 2f * plane[1] * plane[1];
            reflectionMat.m12 =      -2f * plane[1] * plane[2];
            reflectionMat.m13 =      -2f * plane[3] * plane[1];
            reflectionMat.m20 =      -2f * plane[2] * plane[0];
            reflectionMat.m21 =      -2f * plane[2] * plane[1];
            reflectionMat.m22 =  1f - 2f * plane[2] * plane[2];
            reflectionMat.m23 =      -2f * plane[3] * plane[2];
            reflectionMat.m30 = 0f; reflectionMat.m31 = 0f;
            reflectionMat.m32 = 0f; reflectionMat.m33 = 1f;
        }

        private static void MakeProjectionMatrixOblique(ref Matrix4x4 matrix, Vector4 clipPlane)
        {
            // Lengyel oblique near-clip algorithm. Modifies row 2 (the Z row) of the
            // projection matrix so the near plane coincides with the mirror surface.
            // Unity Matrix4x4 single-index: matrix[i] = matrix[row = i%4, col = i/4].
            var q = new Vector4(
                (Mathf.Sign(clipPlane.x) + matrix[8])  / matrix[0],
                (Mathf.Sign(clipPlane.y) + matrix[9])  / matrix[5],
                -1f,
                (1f + matrix[10]) / matrix[14]
            );
            var c      = clipPlane * (2f / Vector3.Dot(clipPlane, q));
            matrix[2]  = c.x;
            matrix[6]  = c.y;
            matrix[10] = c.z + 1f;
            matrix[14] = c.w;
        }
    }
}
