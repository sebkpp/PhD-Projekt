using System.Collections;
using Application.Scripts.Avatar;
using Fusion;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Experiment
{
    [RequireComponent(typeof(NetworkObject))]
    public class ExperimentController : NetworkBehaviour
    {
        public int ExperimentId { get; private set; }

        [SerializeField] private DataManager dataManager;

        [Header("Player Positions")]
        [SerializeField] private Transform localPlayerRig;
        [SerializeField] private Transform onboardingPosition;
        [SerializeField] private Transform experimentPositionOne;
        [SerializeField] private Transform experimentPositionTwo;


        //Events
        public delegate void GenderChange(int playerId, Gender gender);
        public static event GenderChange OnChangeGender;

        public delegate void AvatarChange(int playerId, AvatarOptions opt = AvatarOptions.None);
        public static event AvatarChange OnChangeAvatarOptions; //Hands vs Full-Body

        public static UnityEvent OnStartExperiment = new();

        private void OnEnable()
        {
            OnStartExperiment.AddListener(TransitionToExperiment);
        }

        private void OnDisable()
        {
            OnStartExperiment.RemoveListener(TransitionToExperiment);
        }

        private void Start()
        {
            ExperimentId = -1;
        }

        public override void Spawned()
        {
            if (dataManager != null)
                dataManager.SetLocalPlayerId(Runner.LocalPlayer.PlayerId);
        }

        /// <summary>
        /// Sets the experiment id if the experiment didn't start. It returns if the id was valid and saved or not.
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public bool SetExperimentId(int id)
        {
            if (id > 0)
            {
                ExperimentId = id;
                return true;
            }
            else
            {
                Debug.LogError("Invalid ID");
                return false;
            }
        }
        public void StartExperiment()
        {
            if (ExperimentId == -1)
            {
                Debug.LogError("Set experiment id to start experiment");
            }
            else
            {
                RPC_StartStudy();
            }
        }
        [Rpc]
        private void RPC_StartStudy()
        {
            OnStartExperiment?.Invoke();
        }

        private void TransitionToExperiment()
        {
            StartCoroutine(TransitionToExperiment_Coroutine());
        }

        private IEnumerator TransitionToExperiment_Coroutine()
        {
            if (localPlayerRig == null) yield break;

            Fader fader = localPlayerRig.GetComponentInChildren<Fader>();
            if (fader != null)
            {
                fader.FadeTransition();
                yield return new WaitUntil(() => fader.FadedIn);
            }

            // PlayerId 1 → position one, PlayerId 2 → position two
            Transform expPosition = Runner.LocalPlayer.PlayerId == 1
                ? experimentPositionOne
                : experimentPositionTwo;

            if (expPosition != null)
                localPlayerRig.SetPositionAndRotation(expPosition.position, expPosition.rotation);
        }

        #region ChangeVisualsServer

        public void ChangePlayerGender(PlayerRef player, Gender newGender)
        {
            if (player.IsNone) return;

            RPC_ChangeGender(player, newGender); //RPC all players
        }
        public void ChangeAvatarOptions(AvatarOptions opt)
        {
            RPC_ChangeAvatarOptions(opt);
        }
        public void ChangeHandVisuals(HandVisuals opt)
        {
            RPC_ChangeHandVisuals(opt);
        }

        #endregion

        #region ChangeVisualsClients
        [Rpc]
        private void RPC_ChangeGender(PlayerRef player, Gender newGender)
        {
            OnChangeGender?.Invoke(player.PlayerId, newGender);
        }
        [Rpc]
        private void RPC_ChangeAvatarOptions(AvatarOptions opt)
        {
            if (!Runner.IsPlayer) return;

            Debug.Log("Changing Avatar to " + opt);
            OnChangeAvatarOptions?.Invoke(-1, opt);
        }
        [Rpc]
        private void RPC_ChangeHandVisuals(HandVisuals opt)
        {
            if (!Runner.IsPlayer) return;

            Debug.Log("Changing visualisation to " + opt);
            //TODO
        }


        #endregion
    }

}
