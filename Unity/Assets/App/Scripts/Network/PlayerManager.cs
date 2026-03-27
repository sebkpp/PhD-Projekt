using System;
using System.Collections.Generic;
using Fusion;
using Fusion.Sockets;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Network
{
    public class PlayerManager : NetworkBehaviour, INetworkRunnerCallbacks
    {
        #region ##### UNTIY INSPECTOR #####

        private List<PlayerRef> _playerIds = new();
        
        [SerializeField] private UnityEvent<PlayerRef> playerJoined;
        [SerializeField] private UnityEvent<PlayerRef> playerLeft;
        
        #endregion

        #region ##### PLAYER GETTER ####
        
        public PlayerRef GetPlayerRefById(int id)
        {
            // if (_playerIds.ContainsKey(id))
            //     return _playerIds[id];
            // else
                return new();
        }

        #endregion
        

        #region ##### INetworkCallbacks #####

        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"<color=#ADD8E6>[Network]</color> New player joined");

            if (runner.Topology == Topologies.ClientServer)
            {
                // The user's prefab has to be spawned by the host
                if (!runner.IsServer) return;
            
                if (Object.HasStateAuthority)
                {
                    _playerIds.Add(player); //Manager = 1, Player1 = 2, Player2 = 3
                    playerJoined?.Invoke(player);
                }
            }
        }

        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            if (runner.Topology == Topologies.ClientServer)
            {
                // Find and remove the players avatar (only the host would have stored the spawned game object)
                if (Object.HasStateAuthority)
                {
                    _playerIds.Remove(player);
                }
                
                // Despawn the user object upon disconnection
                playerLeft.Invoke(player);
            }
        }

        #endregion

        #region ##### UNUSED NETWORK CALLBACKS #####
        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnInput(NetworkRunner runner, NetworkInput input) { }
        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }
        public void OnShutdown(NetworkRunner runner, ShutdownReason shutdownReason) { }
        // ReSharper disable once Unity.IncorrectMethodSignature
        public void OnConnectedToServer(NetworkRunner runner) { }
        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason) { }
        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token) { }
        public void OnConnectFailed(NetworkRunner runner, NetAddress remoteAddress, NetConnectFailedReason reason) { }
        public void OnUserSimulationMessage(NetworkRunner runner, SimulationMessagePtr message) { }
        public void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList) { }
        public void OnCustomAuthenticationResponse(NetworkRunner runner, Dictionary<string, object> data) { }
        public void OnHostMigration(NetworkRunner runner, HostMigrationToken hostMigrationToken) { }
        public void OnReliableDataReceived(NetworkRunner runner, PlayerRef player, ReliableKey key, ArraySegment<byte> data) { }
        public void OnReliableDataProgress(NetworkRunner runner, PlayerRef player, ReliableKey key, float progress) { }
        public void OnSceneLoadDone(NetworkRunner runner) { }
        public void OnSceneLoadStart(NetworkRunner runner) { }
        #endregion
    }
}