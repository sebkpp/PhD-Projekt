using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Packages.Mirror
{
    /// <summary>
    /// URP Renderer Feature for planar VR mirror reflections.
    ///
    /// Setup:
    ///   1. Open your URP Renderer asset (e.g. PC_Renderer).
    ///   2. Add Renderer Feature → "Mirror Renderer Feature".
    ///   3. The feature automatically renders all active Mirror components
    ///      in the scene before opaque geometry.
    /// </summary>
    public class MirrorRendererFeature : ScriptableRendererFeature
    {
        private MirrorRenderPass _pass;

        public override void Create()
        {
            _pass = new MirrorRenderPass
            {
                renderPassEvent = RenderPassEvent.BeforeRenderingOpaques
            };
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData data)
        {
            if (!UnityEngine.Application.isPlaying) return;
            if (data.cameraData.camera.CompareTag("PortalCam")) return;
            renderer.EnqueuePass(_pass);
        }

        protected override void Dispose(bool disposing) { }
    }
}
