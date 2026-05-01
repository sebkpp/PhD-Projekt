namespace Application.Scripts.Experiment
{
    public enum AvatarOptions
    {
        FullBody, Hands, None
    }
    
    public enum HandVisuals
    {
        None,
        InnerHand,
        OuterHand,
        SeeThrough,
        FingerColor,
        ObjectColor,
        TwoHands,
        InnerHandReactiveAffordance,
        OuterHandReactiveAffordance
    }

    public struct StudyVariables
    {
        public AvatarOptions avatarOrHands;
        public HandVisuals handVisuals;
    }
}
