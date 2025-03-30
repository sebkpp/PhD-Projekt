using Application.Scripts.Network.Input;

namespace Application.Scripts.Interaction
{
    public interface IXRInputState<TTransform, THand>
    where TTransform : ITransformState
    {
        // Player Area, e.g., for teleportation
        public TTransform PlayArea { get; set; }
        
        // Head
        public TTransform Head { get; set; }

        // Left Hand
        public THand LeftHand { get; set; }

        // Right Hand
        public THand RightHand { get; set; }
    }
}