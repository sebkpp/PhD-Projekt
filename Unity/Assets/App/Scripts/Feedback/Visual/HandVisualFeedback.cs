using Application.Scripts.Feedback.Data;
using Application.Scripts.Network.Interactable;
using UnityEngine;

namespace Application.Scripts.Feedback.Visual
{
    /// <summary>
    /// Implements IVisualFeedbackProvider.
    /// Reads a StimulusDefinition ScriptableObject by stimulus name and:
    ///   - Sets HandRenderingMode on HandRenderingController (IH/OH)
    ///   - Applies MaterialPropertyBlock color mapping for FC/OC techniques
    /// </summary>
    [RequireComponent(typeof(HandRenderingController))]
    public class HandVisualFeedback : MonoBehaviour, IVisualFeedbackProvider
    {
        private HandRenderingController _renderingController;
        private StimulusDefinition _activeDef;
        private Renderer _targetRenderer;
        private MaterialPropertyBlock _mpb;
        private bool _isLeft;

        private void Awake()
        {
            _renderingController = GetComponent<HandRenderingController>();
            _mpb = new MaterialPropertyBlock();
        }

        public void Activate(TrialSlotStimulusData stimulus, NetworkGrabbableObject heldObject, bool isLeft)
        {
            _isLeft = isLeft;
            string visualName = stimulus.GetVisualName() ?? stimulus.stimulus?.name;
            if (string.IsNullOrEmpty(visualName))
            {
                Debug.LogWarning("[HandVisualFeedback] No visual name in stimulus.");
                return;
            }

            _activeDef = Resources.Load<StimulusDefinition>($"Stimuli/{visualName}");
            if (_activeDef == null)
            {
                Debug.LogWarning($"[HandVisualFeedback] StimulusDefinition not found: Stimuli/{visualName}");
                return;
            }

            // Set rendering mode (IH/OH)
            Collider heldCollider = heldObject != null
                ? heldObject.GetComponentInChildren<Collider>()
                : null;
            _renderingController.SetMode(_activeDef.renderingMode, heldCollider, isLeft);

            // Prepare color mapping renderer
            if (_activeDef.technique == VisualTechnique.ColorMapping)
            {
                _targetRenderer = _activeDef.target == FeedbackTarget.Object
                    ? heldObject?.GetComponentInChildren<Renderer>()
                    : GetComponentInParent<SkinnedMeshRenderer>();

                if (_targetRenderer != null)
                    _targetRenderer.GetPropertyBlock(_mpb);
            }
        }

        public void Deactivate()
        {
            if (_renderingController != null)
                _renderingController.SetMode(HandRenderingMode.IH, null, _isLeft);

            if (_targetRenderer != null)
            {
                _targetRenderer.SetPropertyBlock(null);
                _targetRenderer = null;
            }

            _activeDef = null;
        }

        public void OnPhase(HandoverPhase phase) { }

        public void UpdateGrip(float giverGrip, float receiverGrip)
        {
            if (_activeDef == null || _activeDef.technique != VisualTechnique.ColorMapping) return;
            if (_targetRenderer == null) return;

            float grip = _isLeft ? giverGrip : receiverGrip;

            Color color = _activeDef.colorGradient != null
                ? _activeDef.colorGradient.Evaluate(grip)
                : Color.Lerp(Color.white, Color.red, grip);

            _mpb.SetColor(_activeDef.colorShaderProperty, color);
            _targetRenderer.SetPropertyBlock(_mpb);
        }
    }
}
