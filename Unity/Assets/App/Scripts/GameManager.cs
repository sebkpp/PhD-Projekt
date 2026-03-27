using System.Collections;
using UnityEngine;
using Application.Scripts.Avatar;
using Application.Scripts.Experiment;

namespace Application.Scripts
{
    public class GameManager : MonoBehaviour
    {
        [SerializeField] private Transform localPlayerRig;

        [Header("Manager positions")]
        [SerializeField] private Transform managerSpawnPoint;
        [SerializeField] private Transform managerExpPoint;

        [Header("Players positions")]
        [SerializeField] private Transform onboardingPosition;
        [SerializeField] private Transform experimentPositionOne;
        [SerializeField] private Transform experimentPositionTwo;

        public PlayerObject LocalPlayerObject { get; private set; }

        private void OnEnable()
        {
            ExperimentController.OnStartExperiment.AddListener(TransitionToExperiment);
        }

        public Transform GetSpawnPosition(bool isManager) { return isManager ? managerSpawnPoint : onboardingPosition; }
        public void SetLocalPlayer(PlayerObject playerObj, bool isManager)
        {
            if (LocalPlayerObject != null) return; //already saved

            LocalPlayerObject = playerObj;

            if (isManager)
                localPlayerRig.gameObject.SetActive(false);
        }

        private void TransitionToExperiment()
        {
            if (LocalPlayerObject.IsManager)
                LocalPlayerObject.transform.SetPositionAndRotation(managerExpPoint.position, managerExpPoint.rotation);

            else
                StartCoroutine(TransitionToExperiment_Coroutine());

        }
        private IEnumerator TransitionToExperiment_Coroutine()
        {
            Fader fader = localPlayerRig.GetComponentInChildren<Fader>();
            if (fader != null)
            {
                //Start fade in transition
                fader.FadeTransition();
                yield return new WaitUntil(() => fader.FadedIn);
            }

            //Hide avatar
            if (LocalPlayerObject.PlayerVisuals != null)
                LocalPlayerObject.PlayerVisuals.SetAvatarVisibility(false);


            //Translate Players            
            Transform expPosition = LocalPlayerObject.PlayerId == 2 ? experimentPositionOne : experimentPositionTwo;
            localPlayerRig.SetPositionAndRotation(expPosition.position, expPosition.rotation);

            //Show avatar
            if (LocalPlayerObject.PlayerVisuals != null)
                LocalPlayerObject.PlayerVisuals.SetAvatarVisibility(true);
        }
    }
}