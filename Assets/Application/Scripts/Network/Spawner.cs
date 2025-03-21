using System.Collections.Generic;
using System.Linq;
using Application.Scripts.Avatar_rigging;
using Fusion;
using UnityEngine;
using UnityEngine.Events;

namespace Managers
{
    public class Spawner : SimulationBehaviour, IPlayerJoined, IPlayerLeft
    {
        [SerializeField] private Transform _spawnPoint_P1;
        [SerializeField] private Transform _spawnPoint_P2;

        [SerializeField] private NetworkObject _avatarPrefabMale;
        [SerializeField] private NetworkObject _avatarPrefabFemale;

        [SerializeField] private UnityEvent<AvatarLookup> avatarSpawned;
        
        private Dictionary<PlayerRef, NetworkObject> _spawnedAvatars = new Dictionary<PlayerRef, NetworkObject>();

        public void PlayerJoined(PlayerRef player)
        {
            
            Debug.Log($"<color=yellow>[ConnectionManager] OnPlayerJoinedHostMode called for player {player.PlayerId}</color>");
            Debug.Log($"<color=yellow>[ConnectionManager] Is Server: {Runner.IsServer}</color>");
            
            var playerCount = Runner.ActivePlayers.Count();
            Debug.Log($"<color=yellow>[ConnectionManager] Active players: {playerCount}</color>");
            if (playerCount > 2)
            {
                Debug.LogWarning($"<color=red>[ConnectionManager] Too many players: {playerCount}</color>");
                return;
            }
            
            if (playerCount == 1 && player == Runner.LocalPlayer)
            {
                   Vector3 spawnPosition = _spawnPoint_P1 != null ? _spawnPoint_P1.position : Vector3.up * 2; Quaternion spawnRotation = _spawnPoint_P1 != null ? _spawnPoint_P1.rotation : Quaternion.identity;
                   NetworkObject networkPlayerObject = Runner.Spawn(_avatarPrefabMale, spawnPosition, spawnRotation, player);
                   networkPlayerObject.gameObject.name = $"VRavatar_{player.PlayerId}";
                   _spawnedAvatars.Add(player, networkPlayerObject);
                   Debug.Log($"<color=green>[ConnectionManager] Spawned MALE avatar for player {player.PlayerId}</color>");
                   
                   avatarSpawned?.Invoke(networkPlayerObject.GetComponent<AvatarLookup>());
            }

            else if (playerCount == 2 && player == Runner.LocalPlayer)
            {
                Vector3 spawnPosition = _spawnPoint_P2 != null ? _spawnPoint_P2.position : Vector3.up * 2; Quaternion spawnRotation = _spawnPoint_P2 != null ? _spawnPoint_P2.rotation : Quaternion.identity;
                NetworkObject networkPlayerObject = Runner.Spawn(_avatarPrefabFemale, spawnPosition, spawnRotation, player);
                networkPlayerObject.gameObject.name = $"VRavatar_{player.PlayerId}";
                _spawnedAvatars.Add(player, networkPlayerObject); 
                Debug.Log($"<color=green>[ConnectionManager] Spawned FEMALE avatar for player {player.PlayerId}</color>");
                
                avatarSpawned?.Invoke(networkPlayerObject.GetComponent<AvatarLookup>());
            }
                
            Debug.Log($"Spawned local avatar for player {player.PlayerId}");
        }

        public void PlayerLeft(PlayerRef player)
        {
            Debug.Log($"$Player {player.PlayerId} left");

            if (_spawnedAvatars.TryGetValue(player, out NetworkObject networkObject))
            {
                Runner.Despawn(networkObject);
                _spawnedAvatars.Remove(player);
            }
        }
    }
}
