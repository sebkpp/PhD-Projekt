using Application.Scripts.Feedback.Data;
using Application.Scripts.Network.Interactable;

namespace Application.Scripts.Feedback
{
    public interface IVisualFeedbackProvider
    {
        /// <summary>
        /// Activates this visual feedback for the given stimulus on the given held object.
        /// isLeft: which hand side is grabbing.
        /// </summary>
        void Activate(TrialSlotStimulusData stimulus, NetworkGrabbableObject heldObject, bool isLeft);

        void Deactivate();

        void OnPhase(HandoverPhase phase);

        /// <summary>Called every frame while active. giverGrip and receiverGrip are 0-1.</summary>
        void UpdateGrip(float giverGrip, float receiverGrip);
    }
}
