using Application.Scripts.Feedback.Data;

namespace Application.Scripts.Feedback
{
    public interface ITactileFeedbackProvider
    {
        void Activate(TactileStimulusData config);
        void Deactivate();
        void OnPhase(HandoverPhase phase);
        void UpdateGrip(float ownGrip);
    }
}
