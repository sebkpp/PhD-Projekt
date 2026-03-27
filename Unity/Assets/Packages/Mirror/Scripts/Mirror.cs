using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.XR;
using RenderPipeline = UnityEngine.Rendering.RenderPipelineManager;

public class Mirror : MonoBehaviour
{
    #region Variables

    // Public variables
    [Header("Main Settings")] public Vector3 projectionDirection = Vector3.forward;

    public LayerMask mLayerMask = -1; // Set the layermask for the portal camera
    public int mTextureSize = 1024; // The texture size (resolution)
    public bool useStereo = true;


    [Header("Advanced Settings")]
    //clipping & culling
    public float mClipPlaneOffset = 0.001f;

    public float nearClipLimit = 0.2f;

    // Texture settings
    public bool mDisablePixelLights = true;
    public int mFramesNeededToUpdate;

    // public class ProjectionMatrizes
    // {
    //     public Matrix4x4 left = Matrix4x4.identity;
    //     public Matrix4x4 right = Matrix4x4.identity;

    //     public ProjectionMatrizes()
    //     {
    //         left = Matrix4x4.identity;
    //         right = Matrix4x4.identity;
    //     }
    // }


    // Private variables
    private readonly Dictionary<Camera, Camera> _mPortalCameras = new Dictionary<Camera, Camera>();
    // private Dictionary<Camera, ProjectionMatrizes> m_PortalCamerasProjectionMatrix = new Dictionary<Camera, ProjectionMatrizes>();


    private int _mFrameCounter;
    private static bool _sInsideRendering; // To prevent recursion
    private List<XRNodeState> _nodeStates = new List<XRNodeState>();

    private RenderTexture _mPortalTextureLeft;
    private RenderTexture _mPortalTextureRight;
    private int _mOldReflectionTextureSize;

    private InputDevice _hmdInputDevice;
    public Vector3 leftEyeRotationOffset;
    public Vector3 rightEyeRotationOffset;

    #endregion

    #region Methods

    private void OnEnable()
    {
        RenderPipeline.beginCameraRendering += UpdateCamera;
    }

    private void OnDisable()
    {
        RenderPipeline.beginCameraRendering -= UpdateCamera;


        // Cleanup all the objects we possibly have created
        if (_mPortalTextureLeft)
        {
            DestroyImmediate(_mPortalTextureLeft);
            _mPortalTextureLeft = null;
        }

        if (_mPortalTextureRight)
        {
            DestroyImmediate(_mPortalTextureRight);
            _mPortalTextureRight = null;
        }

        foreach (var kvp in _mPortalCameras)
            DestroyImmediate(kvp.Value.gameObject);

        _mPortalCameras.Clear();
    }

    #endregion

    #region Functions

    public void EnableLayer(string layerName)
    {
        mLayerMask |= 1 << LayerMask.NameToLayer(layerName);
    }

    public void DisableLayer(string layerName)
    {
        mLayerMask &= ~(1 << LayerMask.NameToLayer(layerName));
    }

    private void UpdateCamera(ScriptableRenderContext src, Camera camera)
    {
        useStereo = camera.stereoEnabled;
        

        if ((camera.cameraType == CameraType.Game || camera.cameraType == CameraType.SceneView) &&
            camera.tag != "PortalCam" && UnityEngine.Application.isPlaying) // is the current camera eligeble for portalling?
        {
            
            if (_mFrameCounter > 0) // update over how many frames?
            {
                _mFrameCounter--;
                return;
            }

            var rend = GetComponent<Renderer>();

            if (!enabled || !rend || !rend.sharedMaterial || !rend.enabled) // <<<< Why does the renderer NEED to have a shared material??
                return;

            // Safeguard from recursive reflections.
            if (_sInsideRendering)
                return;
            _sInsideRendering = true;

            _mFrameCounter = mFramesNeededToUpdate;

            // Render the camera
            RenderCamera(camera, rend, Camera.StereoscopicEye.Left, ref _mPortalTextureLeft, src);
            if (useStereo)
                //Debug.Log("Detected StereoMode!!"); // works
                RenderCamera(camera, rend, Camera.StereoscopicEye.Right, ref _mPortalTextureRight, src);
        }
    }

    private void RenderCamera(Camera camera, Renderer rend, Camera.StereoscopicEye eye, ref RenderTexture portalTexture, ScriptableRenderContext src)
    {
        Camera portalCamera = null;

        CreatePortalCamera(camera, eye, out portalCamera, ref portalTexture);
        // Create the camera that will render the reflection
        CopyCameraProperties(camera, portalCamera); // Copy the properties of the (player) camera

        // find out the reflection plane: position and normal in world space
        var pos = transform.position; //portalRenderPlane.transform.forward;//
        var
            normal = transform.TransformDirection(
                projectionDirection); // Alex: This is done because sometimes the object reflection direction does not align with what was the default (transform.forward), in this way, the user can specify this.
        //normal.Normalize(); // Alex: normalize in case someone enters a non-normalized vector. Turned off for now because it is a fun effect :P

        // Optionally disable pixel lights for reflection
        var oldPixelLightCount = QualitySettings.pixelLightCount;
        if (mDisablePixelLights)
            QualitySettings.pixelLightCount = 0;

        // Reflect camera around reflection plane
        var d = -Vector3.Dot(normal, pos) - mClipPlaneOffset;
        var reflectionPlane = new Vector4(normal.x, normal.y, normal.z, d);

        var reflection = Matrix4x4.identity;
        CalculateReflectionMatrix(ref reflection, reflectionPlane);

        // Calculate the eye offsets
        Vector3 worldEyePosition;
        Quaternion worldEyeRotation;

        if (useStereo)
        {
            // Get hmd and eye positions
            if (!_hmdInputDevice.isValid)
            {
                var devs = new List<InputDevice>();
                InputDevices.GetDevicesWithCharacteristics(InputDeviceCharacteristics.HeadMounted, devs);
                _hmdInputDevice = devs.FirstOrDefault(dev => (dev.characteristics & InputDeviceCharacteristics.HeadMounted) != 0);
            }

            if (eye == Camera.StereoscopicEye.Left)
            {
                // Set world position left eye
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.leftEyePosition, out var leftEyePositionFromNode);
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.rightEyePosition, out var rightEyePositionFromNode);
                var eyeDistance = Vector3.Distance(leftEyePositionFromNode, rightEyePositionFromNode);
                worldEyePosition = camera.transform.position - camera.transform.right * eyeDistance / 2;

                // Set rotation for left eye
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.centerEyeRotation, out var centerEyeRotationFromNode);
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.leftEyeRotation, out var leftEyeRotationFromNode);
                var leftForwardVector = leftEyeRotationFromNode * Vector3.forward;
                var centerForwardVector = centerEyeRotationFromNode * Vector3.forward;
                leftEyeRotationOffset = Quaternion.FromToRotation(centerForwardVector, leftForwardVector).eulerAngles;
                worldEyeRotation = camera.transform.rotation * Quaternion.Euler(leftEyeRotationOffset);
            }
            else
            {
                // Set world position right eye
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.leftEyePosition, out var leftEyePositionFromNode);
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.rightEyePosition, out var rightEyePositionFromNode);
                var eyeDistance = Vector3.Distance(leftEyePositionFromNode, rightEyePositionFromNode);
                worldEyePosition = camera.transform.position + camera.transform.right * eyeDistance / 2;

                // Set rotation for right eye
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.centerEyeRotation, out var centerEyeRotationFromNode);
                _hmdInputDevice.TryGetFeatureValue(CommonUsages.rightEyeRotation, out var rightEyeRotationFromNode);
                var rightForwardVector = rightEyeRotationFromNode * Vector3.forward;
                var centerForwardVector = centerEyeRotationFromNode * Vector3.forward;
                rightEyeRotationOffset = Quaternion.FromToRotation(centerForwardVector, rightForwardVector).eulerAngles;
                worldEyeRotation = camera.transform.rotation * Quaternion.Euler(rightEyeRotationOffset);
            }
        }
        else
        {
            // No stereo, just take world eye position and rotation from the camera
            worldEyePosition = camera.transform.position;
            worldEyeRotation = camera.transform.rotation;
        }

        // Transform camera to capture reflection correctly
        portalCamera.ResetWorldToCameraMatrix();

        // Set position of portal camera
        portalCamera.transform.position = worldEyePosition;
        portalCamera.transform.rotation = worldEyeRotation;

        // Transform to capture reflection
        portalCamera.worldToCameraMatrix *= reflection;

        // Setup oblique projection matrix so that near plane is our reflection plane. This way we clip everything below/above it for free
        var clipPlane = CameraSpacePlane(portalCamera.worldToCameraMatrix, pos, normal, 1.0f);

        // Get correct projection matrix (in Unity 2020.3, the camera need to render the skybox once to get the correct matrix)
        Matrix4x4 projectionMatrix;
        if (useStereo)
            // Get stereo projection for the current eye
            projectionMatrix = camera.GetStereoProjectionMatrix(eye);
        else
            // Get stereo projection for the camera
            projectionMatrix = camera.projectionMatrix;

        MakeProjectionMatrixOblique(ref projectionMatrix, clipPlane);

        portalCamera.projectionMatrix = projectionMatrix;
        portalCamera.cullingMask = mLayerMask.value;
        portalCamera.targetTexture = portalTexture;

        GL.invertCulling = true;

        try
        {
            UniversalRenderPipeline.RenderSingleCamera(src, portalCamera);
        }
        catch (Exception e)
        {
            Debug.LogWarning("Rendering Mirror-Camera failed!");
        }

        GL.invertCulling = false;
        portalCamera.targetTexture = null;

        // Assign the rendertexture to the material
        var materials = rend.sharedMaterials; // Why only get the shared materials?
        var property = "_ReflectionTex" + eye;

        foreach (var mat in materials)
            if (mat.HasProperty(property))
                mat.SetTexture(property, portalTexture);

        // Restore pixel light count
        if (mDisablePixelLights)
            QualitySettings.pixelLightCount = oldPixelLightCount;

        _sInsideRendering = false;
    }

    private void CreatePortalCamera(Camera currentCamera, Camera.StereoscopicEye eye, out Camera reflectionCamera, ref RenderTexture portalTexture)
    {
        reflectionCamera = null;
        // Create the render texture (if needed)
        if (!portalTexture || _mOldReflectionTextureSize != mTextureSize) // if it doesn't exist or the size has changed
        {
            if (portalTexture) // if it does exist
                DestroyImmediate(portalTexture); // destroy it first

            portalTexture = new RenderTexture(mTextureSize, mTextureSize, 24); // <<<< make buffer size 24??
            portalTexture.name = "__MirrorReflection" + eye + GetInstanceID(); // create the name of the object
            portalTexture.isPowerOfTwo =
                true; // https://docs.unity3d.com/Manual/Textures.html: Non power of two texture assets can be scaled up at import time using the Non Power of 2 option in the advanced texture type in the import settings. Unity will scale texture contents as requested, and in the game they will behave just like any other texture, so they can still be compressed and very fast to load.
            portalTexture.hideFlags = HideFlags.DontSave; // The object will not be saved to the Scene. It will not be destroyed when a new Scene is loaded.

            portalTexture.antiAliasing = 4; // < <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ResourceIntensive but pretty

            _mOldReflectionTextureSize = mTextureSize; // save the old texture size
        }

        // Create camera with the render texture
        if (!_mPortalCameras.TryGetValue(currentCamera, out reflectionCamera)
        ) // if it does not yet exist in the dictionary, create it. If it does, assign it. (catch both not-in-dictionary and in-dictionary-but-deleted-GO)
        {
            var go = new GameObject("Mirror Reflection Camera id" + GetInstanceID() + " for " + currentCamera.GetInstanceID(), typeof(Camera),
                typeof(Skybox)); // create the new game object

            reflectionCamera = go.GetComponent<Camera>();
            reflectionCamera.enabled = false;
            reflectionCamera.transform.position = transform.position;
            reflectionCamera.transform.rotation = transform.rotation;
            reflectionCamera.tag = "PortalCam"; // Tag it as a portal camera so it doesn't participate in the additional CameraRender function
            //portalCamera.gameObject.AddComponent<FlareLayer>(); // Adds a flare layer to make Lens Flares appear in the image?? disabled for now
            go.hideFlags = HideFlags.DontSave; // The object will not be saved to the Scene. It will not be destroyed when a new Scene is loaded.

            _mPortalCameras.Add(currentCamera, reflectionCamera); // add the newly created camera to the dictionary
        }

        // ProjectionMatrizes reflectionProjectionMatrizes = new ProjectionMatrizes(); // Saving ProjectionMatrizes for left and right
        // if (!m_PortalCamerasProjectionMatrix.TryGetValue(currentCamera, out _reflectionProjectionMatrizes))
        // {
        //     //Valve.VR.EVREye valveEyes = (eye == Camera.StereoscopicEye.Left) ? Valve.VR.EVREye.Eye_Left : Valve.VR.EVREye.Eye_Right;
        //     reflectionProjectionMatrizes.left = GetSteamVRProjectionMatrix(currentCamera, Valve.VR.EVREye.Eye_Left);
        //     reflectionProjectionMatrizes.right = GetSteamVRProjectionMatrix(currentCamera, Valve.VR.EVREye.Eye_Right);
        //     m_PortalCamerasProjectionMatrix.Add(currentCamera, reflectionProjectionMatrizes);
        //     _reflectionProjectionMatrizes = reflectionProjectionMatrizes;
        // }
    }

    private void CopyCameraProperties(Camera src, Camera dest)
    {
        if (dest == null) // to prevent errors
            return;

        // set camera to clear the same way as current camera <<< Not really sure what this does, more info: https://docs.unity3d.com/Manual/class-Camera.html
        dest.clearFlags = src.clearFlags;
        dest.backgroundColor = src.backgroundColor;

        if (src.clearFlags == CameraClearFlags.Skybox)
        {
            var sky = src.GetComponent(typeof(Skybox)) as Skybox;
            var mysky = dest.GetComponent(typeof(Skybox)) as Skybox;
            if (!sky || !sky.material)
            {
                mysky.enabled = false;
            }
            else
            {
                mysky.enabled = true;
                mysky.material = sky.material;
            }
        }

        // update other values to match current camera.
        // even if we are supplying custom camera&projection matrices,
        // some of values are used elsewhere (e.g. skybox uses far plane)
        
        //dest.stereoTargetEye = StereoTargetEyeMask.None; // To prevent the camera from following some eye, else this gets fuckey sometimes (e.g. the FOV cant be copied)
        dest.farClipPlane = src.farClipPlane; // 30m is enough in this scene
        dest.nearClipPlane = src.nearClipPlane;
        dest.orthographic = src.orthographic;
        dest.fieldOfView = src.fieldOfView;
        dest.aspect = src.aspect;
        dest.orthographicSize = src.orthographicSize;
        dest.depth = 2;
        //dest.stereoTargetEye = src.stereoTargetEye;
        dest.GetUniversalAdditionalCameraData().renderPostProcessing = true;
    }

    // Given position/normal of the plane, calculates plane in camera space.
    private Vector4 CameraSpacePlane(Matrix4x4 worldToCameraMatrix, Vector3 pos, Vector3 normal, float sideSign)
    {
        var offsetPos = pos + normal * mClipPlaneOffset;
        var cpos = worldToCameraMatrix.MultiplyPoint(offsetPos);
        var cnormal = worldToCameraMatrix.MultiplyVector(normal).normalized * sideSign;
        return new Vector4(cnormal.x, cnormal.y, cnormal.z, -Vector3.Dot(cpos, cnormal));
    }

    #endregion

    #region HelperMethods

    // private Matrix4x4 GetSteamVRProjectionMatrix(Camera cam, EVREye eye)
    // {
    //     // Crashes if called constantly
    //     var proj = SteamVR.instance.hmd.GetProjectionMatrix(eye, cam.nearClipPlane, cam.farClipPlane);
    //     var m = Matrix4x4.identity;
    //     m.m00 = proj.m0;
    //     m.m01 = proj.m1;
    //     m.m02 = proj.m2;
    //     m.m03 = proj.m3;
    //     m.m10 = proj.m4;
    //     m.m11 = proj.m5;
    //     m.m12 = proj.m6;
    //     m.m13 = proj.m7;
    //     m.m20 = proj.m8;
    //     m.m21 = proj.m9;
    //     m.m22 = proj.m10;
    //     m.m23 = proj.m11;
    //     m.m30 = proj.m12;
    //     m.m31 = proj.m13;
    //     m.m32 = proj.m14;
    //     m.m33 = proj.m15;
    //     return m;
    // }

    // Calculates reflection matrix around the given plane
    private static void CalculateReflectionMatrix(ref Matrix4x4 reflectionMat, Vector4 plane)
    {
        reflectionMat.m00 = 1F - 2F * plane[0] * plane[0];
        reflectionMat.m01 = -2F * plane[0] * plane[1];
        reflectionMat.m02 = -2F * plane[0] * plane[2];
        reflectionMat.m03 = -2F * plane[3] * plane[0];

        reflectionMat.m10 = -2F * plane[1] * plane[0];
        reflectionMat.m11 = 1F - 2F * plane[1] * plane[1];
        reflectionMat.m12 = -2F * plane[1] * plane[2];
        reflectionMat.m13 = -2F * plane[3] * plane[1];

        reflectionMat.m20 = -2F * plane[2] * plane[0];
        reflectionMat.m21 = -2F * plane[2] * plane[1];
        reflectionMat.m22 = 1F - 2F * plane[2] * plane[2];
        reflectionMat.m23 = -2F * plane[3] * plane[2];

        reflectionMat.m30 = 0F;
        reflectionMat.m31 = 0F;
        reflectionMat.m32 = 0F;
        reflectionMat.m33 = 1F;
    }

    // Extended sign: returns -1, 0 or 1 based on sign of a
    private static float Sgn(float a)
    {
        if (a > 0.0f) return 1.0f;
        if (a < 0.0f) return -1.0f;
        return 0.0f;
    }

    // Taken from http://www.terathon.com/code/oblique.html
    private static void MakeProjectionMatrixOblique(ref Matrix4x4 matrix, Vector4 clipPlane)
    {
        Vector4 q;

        // Calculate the clip-space corner point opposite the clipping plane
        // as (sgn(clipPlane.x), sgn(clipPlane.y), 1, 1) and
        // transform it into camera space by multiplying it
        // by the inverse of the projection matrix

        q.x = (Sgn(clipPlane.x) + matrix[8]) / matrix[0];
        q.y = (Sgn(clipPlane.y) + matrix[9]) / matrix[5];
        q.z = -1.0F;
        q.w = (1.0F + matrix[10]) / matrix[14];

        // Calculate the scaled plane vector
        var c = clipPlane * (2.0F / Vector3.Dot(clipPlane, q));

        // Replace the third row of the projection matrix
        matrix[2] = c.x;
        matrix[6] = c.y;
        matrix[10] = c.z + 1.0F;
        matrix[14] = c.w;
    }

    #endregion
}