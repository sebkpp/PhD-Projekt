using Application.Scripts.Feedback.Data;
using UnityEngine;

namespace Application.Scripts.Feedback.Tactile
{
    /// <summary>
    /// No-op placeholder for tactile feedback.
    /// Replace this with a hardware-specific implementation (bHaptics, HaptX, custom)
    /// without changing HandoverFeedbackController.
    /// </summary>
    public class TactileFeedbackPlaceholder : MonoBehaviour, ITactileFeedbackProvider
    {
        public void Activate(TactileStimulusData config)
            => Debug.Log($"[Tactile] Activate: pattern={config.pattern} intensity={config.intensity}");

        public void Deactivate()
            => Debug.Log("[Tactile] Deactivate");

        public void OnPhase(HandoverPhase phase)
            => Debug.Log($"[Tactile] Phase: {phase}");

        public void UpdateGrip(float ownGrip) { }
    }
}
