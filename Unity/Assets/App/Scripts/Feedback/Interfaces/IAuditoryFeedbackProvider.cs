using Application.Scripts.Feedback.Data;

namespace Application.Scripts.Feedback
{
    public interface IAuditoryFeedbackProvider
    {
        void Activate(AuditoryStimulusData config);
        void Deactivate();
        void OnPhase(HandoverPhase phase);
        /// <summary>Called every frame. ownGrip: grip of the player this provider belongs to.</summary>
        void UpdateGrip(float ownGrip);
    }
}
