using Photon;
using UnityEngine;

using Fusion;
using UnityEngine;

public class ConnectionManager : MonoBehaviour
{
    public static ConnectionManager Instance;
    private NetworkRunner networkRunner;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private async void Start()
    {
        networkRunner = gameObject.AddComponent<NetworkRunner>();
        networkRunner.ProvideInput = true;

        var result = await networkRunner.StartGame(new StartGameArgs
        {
            GameMode = GameMode.AutoHostOrClient,
            SessionName = "AvatarSession",
            Scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().buildIndex
        });

        if (result.Ok)
        {
            Debug.Log("NetworkRunner gestartet!");
        }
        else
        {
            Debug.LogError($"Fehler beim Start: {result.ShutdownReason}");
        }
    }

    public NetworkRunner GetRunner()
    {
        return networkRunner;
    }
}
