using UnityEngine;

namespace Managers
{
    public class GameManager
    {
        [SerializeField] private Transform[] spawnPositions;

        public Transform GetSpawnPosition(bool isHost)
        {
            // Beispiel: Wähle den ersten Spawnpunkt für den Host, sonst einen zufälligen
            return isHost ? spawnPositions[0] : spawnPositions[UnityEngine.Random.Range(1, spawnPositions.Length)];
        }

        
    }
}