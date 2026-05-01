using System.Collections.Generic;
using Application.Scripts.Avatar.Visuals;
using Application.Scripts.Study;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Network.Player
{
    public class PlayerManager : SimulationBehaviour, IPlayerJoined, IPlayerLeft
    {
        [SerializeField] private NetworkObject   _avatarPrefab;
        [SerializeField] private Transform       _spawnPointP1;
        [SerializeField] private Transform       _spawnPointP2;
        [SerializeField] private BackendService  _backendService;

        private readonly Dictionary<PlayerRef, NetworkObject> _spawnedAvatars = new();
        private SessionState _session;

        private void OnEnable()
        {
            if (_backendService != null)
                _backendService.OnSessionReady.AddListener(OnSessionReady);
        }

        private void OnDisable()
        {
            if (_backendService != null)
                _backendService.OnSessionReady.RemoveListener(OnSessionReady);
        }

        private void OnSessionReady(SessionState session)
        {
            _session = session;
        }

        public void PlayerJoined(PlayerRef player)
        {
            if (player != Runner.LocalPlayer) return;

            Transform spawnPoint = player.PlayerId == 1 ? _spawnPointP1 : _spawnPointP2;
            if (spawnPoint == null)
            {
                Debug.LogError($"[PlayerManager] Spawn point for player {player.PlayerId} is not assigned.");
                return;
            }

            NetworkObject avatar = Runner.Spawn(_avatarPrefab, spawnPoint.position, spawnPoint.rotation, player);
            _spawnedAvatars[player] = avatar;

            string gender = _session?.GetGender(player.PlayerId) ?? "Female";
            PlayerVisuals visuals = avatar.GetComponent<PlayerVisuals>();
            if (visuals != null)
                visuals.SetGender(gender);
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
