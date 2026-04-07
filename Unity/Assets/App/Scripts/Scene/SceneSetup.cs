using Application.Scripts.Avatar;
using Application.Scripts.Avatar.Driver;
using Application.Scripts.Network.Interactable;
using UnityEngine;

namespace Application.Scripts.Scene
{
    /// <summary>
    /// Per-scene configurator. Place on a dedicated scene-level GameObject (not inside any prefab).
    /// Configures prefab instances for the specific needs of this scene at runtime.
    /// Only handles cross-layer wiring that components cannot self-configure.
    /// </summary>
    public class SceneSetup : MonoBehaviour
    {
        [Header("Presence")]
        [SerializeField] private AvatarDriver _avatarDriver;
        [SerializeField] private HardwareRig  _hardwareRig; // assign in Presence-only scenes

        [Header("Multiplayer — Handover")]
        [SerializeField] private HandoverTracker[] _handoverTrackers;
        [SerializeField] private int _testTrialId = 0; // used when no BackendService is present

        private void Awake()
        {
            _avatarDriver?.SetLocalRig(_hardwareRig);

            if (_handoverTrackers != null)
                foreach (var tracker in _handoverTrackers)
                    tracker?.SetTrialId(_testTrialId);
        }
    }
}
