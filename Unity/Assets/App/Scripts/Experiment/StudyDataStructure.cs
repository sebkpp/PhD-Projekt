using System;

namespace Application.Scripts.Experiment
{
    #region StudyData
    [Serializable]
    public struct StudyDataRoot
    {
        public Study[] Data;
    }
    [Serializable]
    public struct Study
    {
        public int StudyId;
        public bool AvatarVisibility;
        //Other study variables
        public Trial[] trials;

    }
    [Serializable]
    public struct Trial
    {
        public int TrialId;
        //Players
        public int giverId;
        public int recieverId;
        //Timestamps
        public string GripTimestamp;
        public string TransportTimestamp;
        public string TransferTimestamp;
        public string TaskTimestamp;
    }
    #endregion

    #region EyeTrackingData
    [Serializable]
    public struct EyeTrackingDataRoot
    {
        public EyeTrackingData[] Data;
    }
    [Serializable]
    public struct EyeTrackingData
    {
        public int TrialId;
        public int PlayerId;
        public Role PlayerRole;
        public CollaborationPhase Phase;
        public TrackedLayers TrackedLayers;
        public string Timestamp;
    }
    [Serializable]
    public struct TrackedLayers
    {
        public string LeftEyeLayer;
        public string RightEyeLayer;
    }

    [Serializable]
    public enum CollaborationPhase
    {
        Inactive = 0,
        Grip = 1,
        Transport = 2,
        Transfer = 3,
        Task = 4
    }
    [Serializable]
    public enum Role
    {
        Giver, Receiver
    }
    #endregion
}