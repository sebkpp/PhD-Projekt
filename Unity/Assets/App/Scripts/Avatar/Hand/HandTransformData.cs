using System;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Avatar.Hand
{
    [Serializable]
    public struct FingerJointTransformData : INetworkStruct
    {
        public Vector3 position;
        public Quaternion rotation;
    }
    
    [Serializable]
    public struct FingerTransformData : INetworkStruct
    {
        public FingerJointTransformData metacarpal;
        public FingerJointTransformData proximal;
        public FingerJointTransformData intermediate;
        public FingerJointTransformData distal;
        public FingerJointTransformData tip;
    }
    
    [Serializable]
    public struct HandTransformData : INetworkStruct
    {
        public Vector3 handPosition;
        public Quaternion handRotation;
        
        public FingerTransformData thumb;
        public FingerTransformData index;
        public FingerTransformData middle;
        public FingerTransformData ring;
        public FingerTransformData pinky;
    }
}