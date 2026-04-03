using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.Universal;

namespace Packages.Mirror
{
    /// <summary>
    /// Retained as a no-op pass so MirrorRendererFeature can still exclude
    /// portal cameras from receiving other renderer features.
    /// Mirror rendering itself is triggered via RenderPipelineManager.beginCameraRendering
    /// in Mirror.cs, which is the only correct place to call SubmitRenderRequest
    /// (outside the active render loop).
    /// </summary>
    internal class MirrorRenderPass : ScriptableRenderPass
    {
        public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData) { }

        public override void OnCameraCleanup(CommandBuffer cmd) { }
    }
}
