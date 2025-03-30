using Application.Scripts.Interaction;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Input
{
    public struct TransformStateNetworked :  INetworkStruct
    {
        public Vector3 Position;
        public Quaternion Rotation;
    }
}