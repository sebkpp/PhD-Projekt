using System.Collections.Generic;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Player
{
    public class PlayerManager : SimulationBehaviour, IPlayerJoined, IPlayerLeft
    {
        [SerializeField] private NetworkObject avatarPrefabP1;
        [SerializeField] private NetworkObject avatarPrefabP2;
        [SerializeField] private Transform spawnPointP1;
        [SerializeField] private Transform spawnPointP2;

        private readonly Dictionary<PlayerRef, NetworkObject> _spawnedAvatars = new();

        public void PlayerJoined(PlayerRef player)
        {
            // In Shared Mode IPlayerJoined fires on all peers for every joining player.
            // Each peer is responsible only for spawning its own avatar.
            if (player != Runner.LocalPlayer) return;

            // Fusion 2 assigns PlayerId sequentially from 1.
            // First player to join → slot P1, second → slot P2.
            bool isFirstSlot = player.PlayerId == 1;
            NetworkObject prefab = isFirstSlot ? avatarPrefabP1 : avatarPrefabP2;
            Transform spawnPoint = isFirstSlot ? spawnPointP1 : spawnPointP2;

            NetworkObject avatar = Runner.Spawn(prefab, spawnPoint.position, spawnPoint.rotation, player);
            _spawnedAvatars[player] = avatar;
        }

        public void PlayerLeft(PlayerRef player)
        {
            if (_spawnedAvatars.TryGetValue(player, out NetworkObject avatar))
            {
                Runner.Despawn(avatar);
                _spawnedAvatars.Remove(player);
            }
        }

        public NetworkObject GetAvatar(PlayerRef player)
        {
            _spawnedAvatars.TryGetValue(player, out NetworkObject avatar);
            return avatar;
        }
    }
}
