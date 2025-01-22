using Fusion;
using UnityEngine;

namespace Managers
{
    public class Spawner : SimulationBehaviour, IPlayerJoined
    {
        [SerializeField] private NetworkObject medicalPrefab;
        [SerializeField] private Transform spawnPoint;

        public void PlayerJoined(PlayerRef player)
        {
            if (medicalPrefab == null || spawnPoint == null)
            {
                Debug.LogError("Prefab or SpawnPoint is not set");
                return;
            }

            Runner.Spawn(medicalPrefab, spawnPoint.position, spawnPoint.rotation, player);
        }
    }
}