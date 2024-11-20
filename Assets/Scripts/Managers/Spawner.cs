using UnityEngine;
namespace Managers

{
    public class Spawner : MonoBehaviour, IPlayerJoined, IPlayerLeft

    /*[SerializeField] private unserPlayerPrefab playerPrefab;
    [Networked, Capacity(2)] private NetworkDic<PlayerRef, Player> Players => default;
    {
        //toDo: Behaviour anpassen/recherchieren, evt. SimulationBehaviour. Was brauchen wir hier?
        //toDo: welche Felder braucht es hier? 
    }

    
    nur Host soll Spwanen erlauben
     private void PlayerJoined(PlayerRef player)
     {
        if (HasStateAuthority)
        {
            NetworkObject playerObject = Runner.Spawn(unserPlayerPrefab, Vector3.up, Quaternion.identity, player)
            Players.Add(player, playerObject.GetComponent<Player>());
        }
     }


     private void PlayerLeft(PlayerRef player)
     {
        if (!HasStateAuthority)
            return;

        if(Players.TryGet(plyer, out Player playerBehaviour))
        {
            Players.remove(player);
            Runner.Despawn(playerBehaviour.Object);
        }
     }

     
     private Vector3 GetSpawnPosition()
     */
}