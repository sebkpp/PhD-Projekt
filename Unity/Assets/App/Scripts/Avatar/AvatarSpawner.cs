using System.Collections.Generic;
using System.Linq;
using Fusion;
using Application.Scripts.Network.Input;
using UnityEngine;
using UnityEngine.Rendering;

namespace Application.Scripts.Avatar
{
    /// <summary>
    /// Spawns player networked avatars in scene
    /// </summary>
    public class AvatarSpawner : Singleton<AvatarSpawner>
    {
        #region ##### UNITY INSPECTOR #####
        
        [Header(" References")]
        [Tooltip("Needed to spawn avatars within the network instance")]
        [SerializeField] private NetworkRunner runner;
        
        [Tooltip("Prefab for the avatar which has to be spawned")]
        [SerializeField] private GameObject avatarPrefab;
        
        [Tooltip("Specify the location where avatars will be spawned")]
        [SerializeField] private Transform spawnOrigin;

        [Tooltip("Avatars are spawned as children of this game object, if empty it will create a new game object")]
        [SerializeField] private Transform userInstances;

        #endregion

        #region ##### PUBLIC PROPERTIES #####

        public Transform UserInstances => userInstances;

        #endregion
        
        #region ##### PRIVATE MEMBER #####

        /// <summary>
        /// Stores the current player-avatars together with there corresponding PlayerID from Network
        /// </summary>
        private SerializedDictionary<PlayerRef, NetworkObject> _activePlayerAvatars;

        #endregion

        #region ##### UNITY MONOBEHAVIOUR #####

        private void Start()
        {
            if (!userInstances) userInstances = new GameObject("UserInstances").transform;

            _activePlayerAvatars = new SerializedDictionary<PlayerRef, NetworkObject>();
        }

        #endregion

        #region ##### PUBLIC METHODS #####

        /// <summary>
        /// Called when a player joins the networked session.
        /// </summary>
        /// <param name="player"></param>
         public void OnPlayerJoined(PlayerRef player)
        {
            //Player Instantiation
            if (avatarPrefab == null)
            {
                Debug.LogError("<Color=Red><a>Missing</a></Color> playerPrefab Reference. " +
                               "Please set it up in GameObject 'Game Manager'", this);
                return;
            }
            
            // if (_activePlayerAvatars.Count == 0) //&& useManager && managerPrefab != null)
            // {
            //     Debug.Log($"<color=#ADD8E6>[Network]</color> SessionMaster Joined. PlayerId: {player.PlayerId}");
            //     // Transform t = gameManager.GetSpawnPosition(true);
            //     // NetworkObject networkPlayerObject = Runner.Spawn(managerPrefab,
            //     //     t.position,
            //     //     t.rotation,
            //     //     player);
            //     //
            //     // networkPlayerObject.transform.SetParent(userInstances);
            //     // networkPlayerObject.gameObject.name = "Manager";
            //     //
            //     // // Keep track of the player avatars so we can remove it when they disconnect
            //     // AddPlayer(player, networkPlayerObject.GetComponent<NetworkRig>());
            // }
            if (avatarPrefab != null)
            {
                Debug.Log($"<color=#ADD8E6>[Network]</color> OnPlayerJoined Host Mode. PlayerId: {player.PlayerId}");
                // We make sure to give the input authority to the connecting player for their user's object

                Transform t = spawnOrigin; //gameManager.GetSpawnPosition(false);
                NetworkObject networkPlayerObject = runner.Spawn(avatarPrefab,
                    t.position,
                    t.rotation,
                    player);
                
                // Keep track of the player avatars so we can remove it when they disconnect
                _activePlayerAvatars.Add(player, networkPlayerObject);
            }
            else
            {
                Debug.LogError($"<color=#ADD8E6>[Network]</color> Player {player.PlayerId} could not be spawned. Check references.");
            }
        }

        public void OnPlayerLeft(PlayerRef player)
        {
            if (_activePlayerAvatars.TryGetValue(player, out NetworkObject networkedAvatar))
            {
                runner.Despawn(networkedAvatar);
            }
            else
            {
                Debug.LogWarning($"<color=yellow>[Network:AvatarSpawn]</color> " +
                                 $"Couldn't find PlayerRef in activeAvatars, Avatar wasn't despawned!");
            }
        }
        
        // ReSharper disable once MemberCanBePrivate.Global
        public IEnumerable<NetworkObject> GetAllActiveAvatars()
        {
            return _activePlayerAvatars.Select(kvp => kvp.Value);
        }

        #endregion
       
        
        
        #region ##### DEBUG #####

        // ReSharper disable once MemberCanBePrivate.Global
        public void EnableDebugMode(bool enabledDebug)
        {
            foreach (NetworkObject playerAvatar in GetAllActiveAvatars())
            {
                NetworkRig avatarRig = playerAvatar.GetComponent<NetworkRig>();
                avatarRig.EnableDebug(enabledDebug);
            }
        }

        #endregion
    }
}
