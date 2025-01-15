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
        [SerializeField] private NetworkObject _avatarPrefab;
        [SerializeField] private Transform _spawnPoint;

        [SerializeField] private GameMode _gameMode = GameMode.Shared;
        [SerializeField] private string _room = "OP";
        [SerializeField] private bool _connectOnStart = true;
        
        private Dictionary<PlayerRef, NetworkObject> _spawnedAvatars = new Dictionary<PlayerRef, NetworkObject>();
        
        private void Awake()
        {
            // Check: existiert Runner?
            _runner = GetComponent<NetworkRunner>();
            if (_runner == null) _runner = gameObject.AddComponent<NetworkRunner>();
            _runner.ProvideInput = true;
        }
        
        private async void Start()
        {
            if (_connectOnStart)
            {
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
                    Debug.LogError($"Kann nicht gestartet werden: {result.ShutdownReason}");
                }
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

        //public GameObject medicalFemale;
        //public GameObject medicalMale;
        public void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"Player {player.PlayerId} joined");
            
            // spawn avatar for local player
            if (player == runner.LocalPlayer)
            {
                Vector3 spawnPosition = _spawnPoint != null ? _spawnPoint.position : Vector3.up * 2; Quaternion spawnRotation = _spawnPoint != null ? _spawnPoint.rotation : Quaternion.identity;
               NetworkObject networkPlayerObject = runner.Spawn(_avatarPrefab, spawnPosition, spawnRotation, player);
               networkPlayerObject.gameObject.name = $"VRavatar_{player.PlayerId}";
               _spawnedAvatars.Add(player, networkPlayerObject);
        
                // Spawn medical male
                // NetworkObject maleAvatar = runner.Spawn(medicalMale, spawnPosition + new Vector3(2f, 0f, 0f), spawnRotation, player);
                // maleAvatar.gameObject.name = $"MedicalMale_{player.PlayerId}";
                // _spawnedAvatars.Add(player, maleAvatar);
                
                
                // Spawn medical female
                // NetworkObject femaleAvatar = runner.Spawn(medicalFemale, spawnPosition, spawnRotation, player);
                // femaleAvatar.gameObject.name = $"MedicalFemale_{player.PlayerId}";
                // _spawnedAvatars.Add(player, femaleAvatar);
                
                Debug.Log($"Spawned local avatar for player {player.PlayerId}");
            }
        }
        public void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"$Player {player.PlayerId} left");

            if (_spawnedAvatars.TryGetValue(player, out NetworkObject networkObject))
            {
                runner.Despawn(networkObject);
                _spawnedAvatars.Remove(player);
            }
        }
        
        /*private async void StartSession()
        {
            var startResult = await _runner.StartGame(new StartGameArgs
            {
                GameMode = GameMode.AutoHostOrClient,
                SessionName = "AvatarSession"
            });

            if (startResult.Ok)
            {
                Debug.Log("Session successfully started!");
            }
            else
            {
                Debug.LogError($"Network error: {startResult.ShutdownReason}");
                OnNetworkErrorEvent?.Invoke(startResult.ShutdownReason.ToString());
            }
        }*/

        /*private void HandlePlayerJoined(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"Player {player.PlayerId} has joined!");
            OnPlayerJoinedEvent?.Invoke(player);
        }*/

        /*private void HandlePlayerLeft(NetworkRunner runner, PlayerRef player)
        {
            Debug.Log($"Player {player.PlayerId} has left.");
            if (_playerAvatars.ContainsKey(player))
            {
                Destroy(_playerAvatars[player]);
                _playerAvatars.Remove(player);
            }

            OnPlayerLeftEvent?.Invoke(player);
        }

        public void RegisterAvatar(PlayerRef player, GameObject avatar)
        {
            if (!_playerAvatars.ContainsKey(player))
            {
                _playerAvatars[player] = avatar;
            }
        }

        public GameObject GetAvatar(PlayerRef player)
        {
            return _playerAvatars.TryGetValue(player, out var avatar) ? avatar : null;
        }

        public async void LoadScene(string sceneName)
        {
            int sceneIndex = SceneManager.GetSceneByName(sceneName).buildIndex;

            if (_runner.IsServer)
            {
                Debug.Log($"Switching to scene: {sceneName}");
                
            }
            else
            {
                Debug.LogWarning("Only the host can change scenes.");
            }
        }

        private void OnDestroy()
        {
            if (_runner != null)
            {
                OnPlayerJoined(_runner, new PlayerRef()); 
                OnPlayerLeft(_runner, new PlayerRef()); 
            }
        }

        private void OnDisable()
        {
            if (_runner != null)
            {
                _runner.Shutdown();
            }
        }

        public NetworkRunner GetRunner()
        {
            return _runner;
        }*/
        
        

        
        
        #region INetworkRunnerCallbacks
        // public void OnPlayerJoined(NetworkRunner runner, PlayerRef player) { }
     
        
        // public void OnPlayerLeft(NetworkRunner runner, PlayerRef player) { }
        #endregion

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



        public void OnObjectExitAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player)
        {
            throw new NotImplementedException();
        }

        public void OnObjectEnterAOI(NetworkRunner runner, NetworkObject obj, PlayerRef player)
        {
            throw new NotImplementedException();
        }
        

        public void OnInput(NetworkRunner runner, NetworkInput input)
        {
            
        }

        public void OnInputMissing(NetworkRunner runner, PlayerRef player, NetworkInput input)
        {
            
        }
        

        public void OnConnectedToServer()
        {
            throw new NotImplementedException();
        }
        

        public void OnConnectRequest(NetworkRunner runner, NetworkRunnerCallbackArgs.ConnectRequest request, byte[] token)
        {
            
        }
        

        public void OnUserSimulationMessage(NetworkRunner runner, SimulationMessagePtr message)
        {
            
        }

        public void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList)
        {
            throw new NotImplementedException();
        }

        public void OnCustomAuthenticationResponse(NetworkRunner runner, Dictionary<string, object> data)
        {
            throw new NotImplementedException();
        }

        public void OnHostMigration(NetworkRunner runner, HostMigrationToken hostMigrationToken)
        {
            throw new NotImplementedException();
        }

        public void OnReliableDataReceived(NetworkRunner runner, PlayerRef player, ReliableKey key, ArraySegment<byte> data)
        {
            throw new NotImplementedException();
        }

        public void OnReliableDataProgress(NetworkRunner runner, PlayerRef player, ReliableKey key, float progress)
        {
            throw new NotImplementedException();
        }

        public void OnSceneLoadDone(NetworkRunner runner)
        {
            
        }

        public void OnSceneLoadStart(NetworkRunner runner)
        {
            
        }
    }
}


