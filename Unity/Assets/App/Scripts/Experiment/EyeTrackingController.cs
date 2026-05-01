using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Application.Scripts.Experiment
{
    public class EyeTrackingController : MonoBehaviour
    {
        [SerializeField] private DataManager _dataManager;
        [SerializeField] private OVREyeGaze leftEye;
        [SerializeField] private OVREyeGaze rightEye;
        [SerializeField] private float trackingSeconds = 0.1f;

        private bool _trackEyes = false;
        private WaitForSeconds _sleep;
        private Coroutine _coroutine;
        private void OnEnable()
        {
            ExperimentController.OnStartExperiment.AddListener(RecordEyes);
        }
        private void RecordEyes()
        {
            _trackEyes = true;
            _coroutine = StartCoroutine(RecordEyeTrackingData());
        }
        private IEnumerator RecordEyeTrackingData()
        {
            _sleep = new WaitForSeconds(trackingSeconds);

            while (_trackEyes)
            {
                TrackedLayers layers = new()
                {
                    LeftEyeLayer = GetEyeTrackingLayers(leftEye),
                    RightEyeLayer = GetEyeTrackingLayers(rightEye)
                };

                _dataManager.OnEyesTracked(layers);
                yield return _sleep;
            }
        }
        public string GetEyeTrackingLayers(OVREyeGaze eye)
        {
            if (Physics.Raycast(
                eye.transform.position,
                eye.transform.TransformDirection(Vector3.forward),
                out RaycastHit hit))
            {
                int layer = hit.collider.gameObject.layer;
                return LayerMask.LayerToName(layer);
            }

            return "None";
        }

        private void OnDisable()
        {
            _trackEyes = false;
            if (_coroutine != null)
                StopCoroutine(_coroutine);
        }
    }
}