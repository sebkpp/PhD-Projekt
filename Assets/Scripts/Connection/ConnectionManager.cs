using Fusion;
using Fusion.Sockets;
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class ConnectionManager : MonoBehaviour
{
    public static ConnectionManager Instance;

    private NetworkRunner networkRunner;
    private Dictionary<PlayerRef, GameObject> playerAvatars = new Dictionary<PlayerRef, GameObject>();

    public event Action<PlayerRef> OnPlayerJoinedEvent;
    public event Action<PlayerRef> OnPlayerLeftEvent;
    public event Action<string> OnNetworkErrorEvent;

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

        networkRunner.SessionListUpdated += OnSessionListUpdated;
        networkRunner.PlayerJoined += OnPlayerJoined;
        networkRunner.PlayerLeft += OnPlayerLeft;

        var joinResult = await networkRunner.JoinSessionLobby(SessionLobby.ClientServer);

        if (!joinResult.Ok)
        {
            Debug.LogWarning("Keine Sitzung gefunden. Erstelle neue Sitzung...");
            StartSession();
        }
    }

    private async void StartSession()
    {
        var startResult = await networkRunner.StartGame(new StartGameArgs
        {
            GameMode = GameMode.AutoHostOrClient,
            SessionName = "AvatarSession",
            Scene = SceneManager.GetActiveScene().buildIndex
        });

        if (startResult.Ok)
        {
            Debug.Log("Sitzung erfolgreich gestartet!");
        }
        else
        {
            Debug.LogError($"Netzwerkfehler: {startResult.ShutdownReason}");
            OnNetworkErrorEvent?.Invoke(startResult.ShutdownReason.ToString());
        }
    }

    private void OnPlayerJoined(NetworkRunner runner, PlayerRef player)
    {
        Debug.Log($"Spieler {player.PlayerId} ist beigetreten!");
        OnPlayerJoinedEvent?.Invoke(player);
    }

    private void OnPlayerLeft(NetworkRunner runner, PlayerRef player)
    {
        Debug.Log($"Spieler {player.PlayerId} hat das Spiel verlassen.");
        if (playerAvatars.ContainsKey(player))
        {
            Destroy(playerAvatars[player]);
            playerAvatars.Remove(player);
        }
        OnPlayerLeftEvent?.Invoke(player);
    }

    private void OnSessionListUpdated(NetworkRunner runner, List<SessionInfo> sessionList)
    {
        Debug.Log("Sitzungsliste aktualisiert.");
        if (sessionList.Count > 0)
        {
            Debug.Log($"Beitreten zu Sitzung {sessionList[0].Name}");
            networkRunner.JoinSession(sessionList[0]);
        }
        else
        {
            Debug.Log("Keine Sitzung gefunden.");
        }
    }

    public void RegisterAvatar(PlayerRef player, GameObject avatar)
    {
        if (!playerAvatars.ContainsKey(player))
        {
            playerAvatars[player] = avatar;
        }
    }

    public GameObject GetAvatar(PlayerRef player)
    {
        return playerAvatars.TryGetValue(player, out var avatar) ? avatar : null;
    }

    public async void LoadScene(string sceneName)
    {
        int sceneIndex = SceneManager.GetSceneByName(sceneName).buildIndex;

        if (networkRunner.IsServer)
        {
            Debug.Log($"Wechsel zur Szene: {sceneName}");
            await networkRunner.SetActiveScene(sceneIndex);
        }
        else
        {
            Debug.LogWarning("Nur der Host kann Szenen wechseln.");
        }
    }

    private void OnDestroy()
    {
        if (networkRunner != null)
        {
            networkRunner.SessionListUpdated -= OnSessionListUpdated;
            networkRunner.PlayerJoined -= OnPlayerJoined;
            networkRunner.PlayerLeft -= OnPlayerLeft;
        }
    }

    private void OnDisable()
    {
        if (networkRunner != null)
        {
            networkRunner.Shutdown();
        }
    }

    public NetworkRunner GetRunner()
    {
        return networkRunner;
    }

    private void OnInput(NetworkRunner runner, NetworkInput input)
    {
        VRPlayerInput vrInput = new VRPlayerInput
        {
            HeadPosition = VRInputManager.HeadPosition,
            HeadRotation = VRInputManager.HeadRotation,
            LeftHandPosition = VRInputManager.LeftHandPosition,
            LeftHandRotation = VRInputManager.LeftHandRotation,
            RightHandPosition = VRInputManager.RightHandPosition,
            RightHandRotation = VRInputManager.RightHandRotation,
            IsGrabbing = VRInputManager.IsGrabbing
        };

        input.Set(vrInput);
    }
}

public struct VRPlayerInput : INetworkInput
{
    public Vector3 HeadPosition;
    public Quaternion HeadRotation;
    public Vector3 LeftHandPosition;
    public Quaternion LeftHandRotation;
    public Vector3 RightHandPosition;
    public Quaternion RightHandRotation;
    public bool IsGrabbing;
}
