using UnityEngine;

namespace Managers

{
    public class Spawner : MonoBehaviour
    {
        public GameObject medicalPrefab;
        public Transform spawnPoint;

        void Start()
        {
            SpawnAvatar();
        }

        private void SpawnAvatar()
        {
            if (medicalPrefab != null)
            {
                Instantiate(medicalPrefab, spawnPoint.position, spawnPoint.rotation);
            }
            else
            {
                Debug.LogError("No avatar prefab assigned");
            }
        }
    }
}

