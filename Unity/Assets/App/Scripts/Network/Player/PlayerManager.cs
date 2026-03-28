using System.Collections.Generic;
using Application.Scripts.Avatar.Visuals;
using Application.Scripts.Network.Experiment;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Player
{
    public class PlayerManager : SimulationBehaviour, IPlayerJoined, IPlayerLeft
    {
        [SerializeField] private NetworkObject _avatarPrefab;
        [SerializeField] private Transform _spawnPointP1;
        [SerializeField] private Transform _spawnPointP2;
        [SerializeField] private ExperimentContext _experimentContext;

        private readonly Dictionary<PlayerRef, NetworkObject> _spawnedAvatars = new();

        public void PlayerJoined(PlayerRef player)
        {
            if (player != Runner.LocalPlayer) return;

            Transform spawnPoint = player.PlayerId == 1 ? _spawnPointP1 : _spawnPointP2;
            NetworkObject avatar = Runner.Spawn(_avatarPrefab, spawnPoint.position, spawnPoint.rotation, player);
            _spawnedAvatars[player] = avatar;

            if (_experimentContext != null)
            {
                string gender = _experimentContext.GetGender(player.PlayerId);
                PlayerVisuals visuals = avatar.GetComponentInChildren<PlayerVisuals>();
                if (visuals != null)
                    visuals.SetGender(gender);
            }
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
