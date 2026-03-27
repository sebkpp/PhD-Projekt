using Application.Scripts.Utils.Extensions;
using Fusion;
using Application.Scripts.Avatar;
using Network.Grasp;
using UnityEngine;
using VirtualGrasp;

namespace Interaction.Grasp
{
    public class GrabHand : MonoBehaviour
    {
        #region ##### UNITY INSPECTOR
        
        [Header("References")]
        [Tooltip("Will be set if not set")]
        [SerializeField] private HardwareHand hand;
        [Header("Info")]
        [SerializeField] [VRHands.Attributes.ReadOnly] private GraspableObject graspedObject;
        
        #endregion

        #region ##### PRIVATE FIELDS #####

        private Vector3 _unGrabPosition;
        private Quaternion _unGrabRotation; 
        private Vector3 _unGrabVelocity;
        private Vector3 _unGrabAngularVelocity;
        private GrabInfo _grabInfo;
        
        #endregion
        
        #region ##### PROPERTIES #####

        public GrabInfo GrabInfo
        {
            get
            {
                if (graspedObject)
                {
                    _grabInfo.grabbedObjectId = graspedObject.networkGrabbable.Id;
                    _grabInfo.localPositionOffset = graspedObject.localPositionOffset;
                    _grabInfo.localRotationOffset = graspedObject.localRotationOffset;
                } 
                else
                {
                    _grabInfo.grabbedObjectId = NetworkBehaviourId.None;
                    _grabInfo.ungrabPosition = _unGrabPosition;
                    _grabInfo.ungrabRotation = _unGrabRotation; 
                    _grabInfo.ungrabVelocity = _unGrabVelocity;
                    _grabInfo.ungrabAngularVelocity = _unGrabAngularVelocity;
                }

                return _grabInfo;
            }
        }

        #endregion
        
        #region ##### UNITY MONOBEHAVIOR #####

        private void Awake()
        {
            hand = GetComponentInParent<HardwareHand>();
        }
        
        private void OnEnable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> Register Grasp Events");
            VG_Controller.OnObjectGrasped.AddListener(GraspObject);
            VG_Controller.OnObjectReleased.AddListener(ReleaseObject);
        }

        private void OnDisable()
        {
            Debug.Log($"<color=#ADD8E6>[Grasp]</color> UnregisterGrasp Events");
            VG_Controller.OnObjectGrasped.RemoveListener(GraspObject);
            VG_Controller.OnObjectReleased.RemoveListener(ReleaseObject);
        }

        private void Update()
        {
            var runner = NetworkRunner.Instances.Count > 0 ? NetworkRunner.Instances[0] : null;
            if (runner != null && runner.IsResimulation) return;

            // if (graspedObject != null && graspedObject.currentGrabber != this)
            // {
            //     // This object as been grabbed by another hand, no need to trigger an releaseObject
            //     graspedObject = null;
            // }
        }

        #endregion

        #region ##### EVENT SUBSCRIPTION #####

        private void GraspObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != hand.side) return;
            
            GraspableObject graspable = graspInfo.m_selectedObject.gameObject.GetComponentInParent<GraspableObject>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to grab object {graspable.gameObject.name} with {gameObject.name}");
            
            if (graspable.Grab(this))
            {
                Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> {graspable.gameObject.name} grasped up by {gameObject.name}");
                graspedObject = graspable;
            }
        }
        
        private void ReleaseObject(VG_HandStatus graspInfo)
        {
            // Check if the ones who is sending the event has the same handedness as us
            if (graspInfo.m_side.ToRigPart() != hand.side) return;

            GraspableObject releasedObject = graspInfo.m_selectedObject.gameObject.GetComponentInParent<GraspableObject>();
            
            Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color>Try to release object {releasedObject.gameObject.name} with {gameObject.name}");
            if (releasedObject.networkGrabbable)
            {
                Transform networkedObjectTransform = releasedObject.networkGrabbable.transform;
                
                _unGrabPosition = networkedObjectTransform.position;
                _unGrabRotation = networkedObjectTransform.rotation;
                _unGrabVelocity = releasedObject.Velocity;
                _unGrabAngularVelocity = releasedObject.AngularVelocity;
            }
            graspedObject.Ungrab(releasedObject.currentGrabber);
            graspedObject = null;
        }

        #endregion
        
    }
}