using System;
using System.Collections.Generic;
using Fusion;
using Fusion.Sockets;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using LogLevel = Fusion.LogLevel;

namespace Application.Scripts.Network
{
    [Flags]
    public enum ConnectionCriterias
    {
        RoomName = 1,
        SessionProperties = 2
    }

    [Serializable]
    public struct StringSessionProperty
    {
        public string propertyName;
        public string value;
    }

    [RequireComponent(typeof(NetworkRunner))]
    public class ConnectionManager : MonoBehaviour, INetworkRunnerCallbacks
    {
        [Header("Room configuration")]
        [SerializeField] private NetworkRunner _runner;
        [SerializeField] private GameMode _gameMode = GameMode.Shared;
        [SerializeField] private string _room = "OP";
        [SerializeField] private bool _connectOnStart = true;
        [SerializeField] private LogLevel _logLevel = LogLevel.Error;

        [Header("Room selection criteria")]
        [SerializeField] private ConnectionCriterias _connectionCriterias = ConnectionCriterias.RoomName;
        [Tooltip("Additional session properties appended when SessionProperties criteria is active")]
        [SerializeField] private List<StringSessionProperty> _additionalSessionProperties = new();
        private Dictionary<string, SessionProperty> _sessionProperties;

        [Header("Room configuration (extended)")]
        [SerializeField] private int _playerCount;

        [Header("Events")]
        public UnityEvent onWillConnect = new();
        public UnityEvent<GameObject> playerSpawned = new();

        [Header("Info")]
        public List<StringSessionProperty> actualSessionProperties = new();

        private void Awake()
        {
            if(_runner == null) _runner = GetComponent<NetworkRunner>();
            _runner.ProvideInput = true;
        }

        private Dictionary<string, SessionProperty> BuildSessionProperties()
        {
            actualSessionProperties = new List<StringSessionProperty>();
            var propDict = new Dictionary<string, SessionProperty>();
            if (_sessionProperties != null)
            {
                foreach (var prop in _sessionProperties)
                {
                    propDict.Add(prop.Key, prop.Value);
                    actualSessionProperties.Add(new StringSessionProperty { propertyName = prop.Key, value = prop.Value.ToString() });
                }
            }
            if (_additionalSessionProperties != null)
            {
                foreach (var p in _additionalSessionProperties)
                {
                    propDict[p.propertyName] = p.value;
                    actualSessionProperties.Add(p);
                }
            }
            return propDict;
        }

        private async void Start()
        {
            if (!_connectOnStart) return;
            try
            {
                onWillConnect?.Invoke();

                var startGameArgs = new StartGameArgs()
                {
                    GameMode = _gameMode,
                    Scene = CurrentSceneInfo(),
                    SceneManager = gameObject.AddComponent<NetworkSceneManagerDefault>(),
                };

                bool useRoomName = (_connectionCriterias & ConnectionCriterias.RoomName) != 0;
                bool useSessionProps = (_connectionCriterias & ConnectionCriterias.SessionProperties) != 0;

                if (useRoomName) startGameArgs.SessionName = _room;
                if (useSessionProps) startGameArgs.SessionProperties = BuildSessionProperties();
                if (_playerCount > 0) startGameArgs.PlayerCount = _playerCount;

                var result = await _runner.StartGame(startGameArgs);
                if (!result.Ok)
                {
                    Debug.LogError($"Couldn't start network Session, Reason: {result.ShutdownReason}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogException(ex);
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
                sceneInfo.AddSceneRef(sceneRef);
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
