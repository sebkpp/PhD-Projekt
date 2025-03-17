using System;
using System.Collections.Generic;
using Fusion;
using Fusion.Sockets;
using UnityEngine;
using UnityEngine.Events;

namespace Managers
{
    public class PlayerManager : NetworkBehaviour, INetworkRunnerCallbacks
    {
        private GameManager gameManager;
        [SerializeField] private NetworkObject _prefabOne;
        [SerializeField] private NetworkObject _prefabTwo;
        [SerializeField] private Transform _userInstances;
        [SerializeField] private bool _useManager;
        [SerializeField] private bool _enableDebug;

        private Dictionary<PlayerRef, GameObject> _players;
        private UnityEvent<PlayerRef> _playerJoinedEvent = new();
        private UnityEvent<PlayerRef> _playerLeftEvent = new();
        private bool _isInitialized;

        public override void Spawned()
        {
            base.Spawned();
            _players = new Dictionary<PlayerRef, GameObject>();
            _isInitialized = true;
        }

        private void Log(string message)
        {
            if (_enableDebug)
                Debug.Log($"<color=#ADD8E6>[PlayerManager]</color> {message}");
        }

        #region Player Management

        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            Log($"Player joined: {player}");

            if (_useManager && _prefabOne != null)
            {
                Transform spawnPoint = gameManager.GetSpawnPosition(false);
                NetworkObject playerObject = runner.Spawn(_prefabOne, spawnPoint.position, spawnPoint.rotation, player);
                
                if (_userInstances != null)
                    playerObject.transform.SetParent(_userInstances);

                playerObject.gameObject.name = $"Player_{player.PlayerId}";
                _players[player] = playerObject.gameObject;

                _playerJoinedEvent.Invoke(player);
            }
        }

        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            if (_players.TryGetValue(player, out var playerObject))
            {
                Log($"Player left: {player}");
                runner.Despawn(playerObject.GetComponent<NetworkObject>());
                _players.Remove(player);
                _playerLeftEvent.Invoke(player);
            }
            else
            {
                Log($"Player {player} left, but no corresponding object was found.");
            }
        }

        public void OnPlayerJoinedHostMode(NetworkRunner runner, PlayerRef playerRef)
        {
            if (!runner.IsServer) return;

            if (_players.Count == 0 && _useManager && _prefabOne != null)
            {
                Transform t = gameManager.GetSpawnPosition(true);
                NetworkObject managerObject = runner.Spawn(_prefabOne, t.position, t.rotation, playerRef);

                if (_userInstances != null)
                    managerObject.transform.SetParent(_userInstances);

                managerObject.gameObject.name = "Manager";
                _players[playerRef] = managerObject.gameObject;

                Log($"SessionMaster joined. PlayerId: {playerRef.PlayerId}");
            }
        }

        public void OnPlayerLeftHostMode(NetworkRunner runner, PlayerRef playerRef)
        {
            if (_players.TryGetValue(playerRef, out var playerObject))
            {
                runner.Despawn(playerObject.GetComponent<NetworkObject>());
                _players.Remove(playerRef);
                Log($"SessionMaster left. PlayerId: {playerRef.PlayerId}");
            }
        }

        #endregion

        #region INetworkRunnerCallbacks Implementation

        public void OnInput(NetworkRunner runner, NetworkInput input) { }
        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }
        public void OnShutdown(NetworkRunner runner, ShutdownReason shutdownReason) => Log($"Runner shutdown: {shutdownReason}");
        public void OnConnectedToServer(NetworkRunner runner) => Log("Connected to server.");
        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason) => Log($"Disconnected from server: {reason}");
        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token) { }
        public void OnConnectFailed(NetworkRunner runner, NetAddress remoteAddress, NetConnectFailedReason reason) => Log($"Connection failed: {reason}");
        public void OnUserSimulationMessage(NetworkRunner runner, SimulationMessagePtr message) { }
        public void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList) => Log($"Session list updated: {sessionList.Count} sessions found.");
        public void OnCustomAuthenticationResponse(NetworkRunner runner, Dictionary<string, object> data) { }
        public void OnHostMigration(NetworkRunner runner, HostMigrationToken hostMigrationToken) { }
        public void OnReliableDataReceived(NetworkRunner runner, PlayerRef player, ReliableKey key, ArraySegment<byte> data) { }
        public void OnReliableDataProgress(NetworkRunner runner, PlayerRef player, ReliableKey key, float progress) { }
        public void OnSceneLoadDone(NetworkRunner runner) { }
        public void OnSceneLoadStart(NetworkRunner runner) { }
        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }

        #endregion
    }
}
