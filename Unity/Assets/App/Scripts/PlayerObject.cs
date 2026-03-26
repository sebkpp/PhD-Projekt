using Fusion;
using Application.Scripts.Avatar;
using UnityEngine;

namespace Application.Scripts
{
    [RequireComponent(typeof(NetworkObject))]
    public class PlayerObject : MonoBehaviour
    {
        [SerializeField] private bool isManager;

        private NetworkObject _netObject;
        private PlayerVisuals _visuals;
        private int _playerId = -1;


        public int PlayerId => _playerId;
        public bool IsManager => isManager;
        public bool IsLocalPlayer { get; private set; }
        public PlayerVisuals PlayerVisuals
        {
            get
            {
                if (_visuals == null)
                    _visuals = GetComponent<PlayerVisuals>();
                return _visuals;
            }
        }

        private void Start()
        {
            if (_playerId != -1) return;

            _netObject = GetComponent<NetworkObject>();
            _playerId = _netObject.Runner.LocalPlayer.PlayerId;

            if (gameObject.name == "Local Player") IsLocalPlayer = true;

            //Save in game
            GameManager manager = FindFirstObjectByType<GameManager>();
            if (manager != null)
                manager.SetLocalPlayer(this, isManager);
        }
    }
}
