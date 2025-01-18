using System;
using System.Collections.Generic;
using Fusion;
using Fusion.Sockets;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Events;
using Task = System.Threading.Tasks.Task;

namespace Connection
{
    [RequireComponent(typeof(NetworkRunner))]
    public class ConnectionManager : MonoBehaviour, INetworkRunnerCallbacks
    {
        public GameMode gameMode = GameMode.Shared;
        public string roomName = "DefaultRoom";
        public bool connectOnStart = true;

        public Dictionary<string, SessionProperty> SessionProperties = new();
        public NetworkRunner networkRunner;
        private INetworkSceneManager _networkSceneManager;

        public UnityEvent onConnected = new();
        public UnityEvent<GameObject> playerSpawned = new();

        private void Awake()
        {
            if (networkRunner == null)
                networkRunner = GetComponent<NetworkRunner>() ?? gameObject.AddComponent<NetworkRunner>();
        }

        private async void Start()
        {
            if (connectOnStart)
                await Connect();
        }

        public async Task Connect()
        {
            if (_networkSceneManager == null)
                _networkSceneManager = gameObject.AddComponent<NetworkSceneManagerDefault>();

            var args = new StartGameArgs
            {
                GameMode = gameMode,
                SessionName = roomName,
                SceneManager = _networkSceneManager,
                PlayerCount = 2 // Beispiel: Maximale Spielerzahl
            };

            await networkRunner.StartGame(args);
        }

        #region INetworkRunnerCallbacks

        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"Player joined: {player}");
            onConnected.Invoke();
        }

        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"Player left: {player}");
        }

        public void OnConnectedToServer(NetworkRunner runner)
        {
            Debug.Log("Connected to server");
        }

        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason)
        {
            Debug.Log($"Disconnected from server: {reason}");
        }

        public void OnConnectFailed(NetworkRunner runner, NetAddress remoteAddress, NetConnectFailedReason reason)
        {
            Debug.LogError($"Connection failed: {reason}");
        }

        public void OnShutdown(NetworkRunner runner, ShutdownReason reason)
        {
            Debug.Log($"Runner shutdown: {reason}");
        }

        public void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList)
        {
            Debug.Log($"Session list updated: {sessionList.Count} sessions found");
        }

        public void OnCustomAuthenticationResponse(NetworkRunner runner, Dictionary<string, object> data) { }

        public void OnHostMigration(NetworkRunner runner, HostMigrationToken hostMigrationToken) { }

        public void OnReliableDataReceived(NetworkRunner runner, PlayerRef player, ReliableKey key, ArraySegment<byte> data) { }

        public void OnReliableDataProgress(NetworkRunner runner, PlayerRef player, ReliableKey key, float progress) { }

        public void OnSceneLoadDone(NetworkRunner runner) { }

        public void OnSceneLoadStart(NetworkRunner runner) { }

        public void OnInput(NetworkRunner runner, NetworkInput input) { }

        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }

        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }

        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }

        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token) { }

        public void OnUserSimulationMessage(NetworkRunner runner, SimulationMessagePtr message) { }

        #endregion
    }
}


