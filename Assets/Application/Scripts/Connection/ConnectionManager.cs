using System;
using System.Collections.Generic;
using Fusion;
using Fusion.Sockets;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Connection
{
    [RequireComponent(typeof(NetworkRunner))]
    public class ConnectionManager : MonoBehaviour, INetworkRunnerCallbacks
    {
        [SerializeField] private NetworkRunner _runner;
        [SerializeField] private GameMode _gameMode = GameMode.Shared;
        [SerializeField] private string _room = "OP";
        [SerializeField] private bool _connectOnStart = true;
        
        private void Awake()
        {
            if(_runner == null) _runner = GetComponent<NetworkRunner>();
            _runner.ProvideInput = true;
        }
        
        private async void Start()
        {
            if (!_connectOnStart) return;
            
            var startGameArgs = new StartGameArgs()
            {
                GameMode = _gameMode,
                SessionName = _room,
                Scene = CurrentSceneInfo(), 
                SceneManager = gameObject.AddComponent<NetworkSceneManagerDefault>()
            };
                
            var result = await _runner.StartGame(startGameArgs);
            if (!result.Ok)
            {
                Debug.LogError($"Couldn't start network Session, Reason: {result.ShutdownReason}");
            }
        }
        
        public virtual NetworkSceneInfo CurrentSceneInfo()
        {
            var activeScene = SceneManager.GetActiveScene();
            SceneRef sceneRef = default;

            if (activeScene.buildIndex < 0 || activeScene.buildIndex >= SceneManager.sceneCountInBuildSettings)
            {
                Debug.LogError("Current scene is not part of the build settings");
            }
            else
            {
                sceneRef = SceneRef.FromIndex(activeScene.buildIndex);
            }

            var sceneInfo = new NetworkSceneInfo();
            if (sceneRef.IsValid)
            {
                sceneInfo.AddSceneRef(sceneRef, LoadSceneMode.Single);
            }
            return sceneInfo;
        }

        #region INetworkRunnerCallbacks (debug log only)
        public void OnConnectedToServer(NetworkRunner runner)
        {
            Debug.Log("<color=#ADD8E6>[Network]</color> OnConnectedToServer");
        }
        public void OnShutdown(NetworkRunner runner, ShutdownReason shutdownReason)
        {
            Debug.Log("<color=#ADD8E6>[Network]</color> Shutdown: " + shutdownReason);
        }
        public void OnDisconnectedFromServer(NetworkRunner runner, NetDisconnectReason reason)
        {
            Debug.Log("<color=#ADD8E6>[Network]</color> OnDisconnectedFromServer: " + reason);
        }
        public void OnConnectFailed(NetworkRunner runner, NetAddress remoteAddress, NetConnectFailedReason reason)
        {
            Debug.Log("<color=#ADD8E6>[Network]</color> OnConnectFailed: " + reason);
        }
        #endregion

        #region Unused INetworkRunnerCallbacks
        
        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player) { }
        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player) { }
        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player) { }
        public void OnInput(NetworkRunner runner, NetworkInput input) { }
        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input) { }
        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token) { }
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


