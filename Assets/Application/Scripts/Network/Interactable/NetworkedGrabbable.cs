using Application.Scripts.InteractableObject;
using Application.Scripts.Network.Interaction;
using Application.Scripts.Utils.Extensions;
using Fusion;
using Fusion.Addons.Physics;
using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Network.Interactable
{
    /// <summary>
    /// Manages the networked state of a grabbable object, synchronizing grab status, position, rotation, and Rigidbody state across the network using Fusion.
    /// Handles authority transfer and extrapolation while grabbing.
    /// </summary>
    public class NetworkedGrabbable : NetworkBehaviour
    {
        /// <summary>
        /// Reference to the NetworkTransform component for position synchronization.
        /// </summary>
        [HideInInspector]
        public NetworkTransform networkTransform;
        
        /// <summary>
        /// Reference to the NetworkRigidbody3D component for physics synchronization.
        /// </summary>
        public NetworkRigidbody3D networkRigidbody;
        
        /// <summary>
        /// Initial kinematic state of the object's Rigidbody saved for late joiners.
        /// </summary>
        [Networked]
        public NetworkBool InitialIsKinematicState { get; set; }
        
        /// <summary>
        /// The current networked grabber holding this object.
        /// </summary>
        [Networked]
        public NetworkedGrabber CurrentGrabber { get; set; }
        
        /// <summary>
        /// Position offset relative to the grabber's hand when grabbed.
        /// </summary>
        [Networked]
        public Vector3 LocalPositionOffset { get; set; }
        
        /// <summary>
        /// Rotation offset relative to the grabber's hand when grabbed.
        /// </summary>
        [Networked]
        public Quaternion LocalRotationOffset { get; set; }

        /// <summary>
        /// Returns true if this object is currently grabbed by a grabber and network object is valid.
        /// </summary>
        public virtual bool IsGrabbed => Object != null && CurrentGrabber != null; // We make sure that we are online before accessing [Networked] var


        /// <summary>
        /// Event invoked on all clients when this object is released/ungrabbed.
        /// </summary>
        [Header("Events")]
        public UnityEvent onDidUngrab = new UnityEvent();
        
        /// <summary>
        /// Event invoked on all clients when this object is grabbed, passing the new NetworkedGrabber.
        /// </summary>
        public UnityEvent<NetworkedGrabber> onDidGrab = new UnityEvent<NetworkedGrabber>();

        /// <summary>
        /// If true, extrapolate the object's position and rotation visually while waiting for authority transfer.
        /// </summary>
        [Header("Advanced options")]
        public bool extrapolateWhileTakingAuthority = true;
        
        /// <summary>
        /// Indicates whether this instance is currently requesting state authority.
        /// </summary>
        public bool isTakingAuthority;

        [HideInInspector]
        public Grabbable grabbable;

        private ChangeDetector _funChangeDetector;
        private ChangeDetector _renderChangeDetector;
        
        /// <summary>
        /// Called when the component awakes. Initializes references and adds a Grabbable component if missing.
        /// </summary>
        private void Awake()
        {
            networkTransform = GetComponent<NetworkTransform>();
            networkRigidbody = GetComponent<NetworkRigidbody3D>();
            grabbable = GetComponent<Grabbable>();
            if (grabbable == null)
            {
                Debug.LogError("NetworkGrabbable requires a Grabbable");// We do not use requireComponent as this classes can be subclassed
                gameObject.AddComponent<Grabbable>();
            }
        }
        
        /// <summary>
        /// Called when the object is spawned on the network.
        /// Saves initial Rigidbody kinematic state and initializes change detectors.
        /// </summary>
        public override void Spawned()
        {
            base.Spawned();

            // Save initial kinematic state for later join player
            if (Object.HasStateAuthority && grabbable.rb)
            {
                InitialIsKinematicState = grabbable.rb.isKinematic;
            }


            // We store the default kinematic state, while it is not affected by NetworkRigidbody logic
            grabbable.expectedIsKinematic = InitialIsKinematicState;

            _funChangeDetector = GetChangeDetector(ChangeDetector.Source.SimulationState);
            _renderChangeDetector = GetChangeDetector(ChangeDetector.Source.SnapshotFrom);
        }

        /// <summary>
        /// Network update loop where grabbing logic and physics locking/unlocking are handled by the state authority.
        /// Also updates the grabbed object's position and rotation following the grabber.
        /// </summary>
        public override void FixedUpdateNetwork()
        {
            if (isTakingAuthority == false && CurrentGrabber && CurrentGrabber.Object.StateAuthority != Object.StateAuthority)
            {
                CurrentGrabber = null;
            }
            // Check if the grabber changed
            if (TryDetectGrabberChange(_funChangeDetector, out var previousGrabber, out var currentGrabber))
            {
                if (previousGrabber)
                {
                    grabbable.UnlockObjectPhysics();
                }
                if (currentGrabber)
                {
                    grabbable.LockObjectPhysics();
                }
            }
            
            if (!IsGrabbed) return;
            
            // Follow grabber, adding position/rotation offsets
            if (CurrentGrabber != null)
                grabbable.Follow(followedTransform: CurrentGrabber.hand.AvatarHand, LocalPositionOffset,
                    LocalRotationOffset);
        }
        
        /// <summary>
        /// Draws gizmos in the editor to visualize the grab point.
        /// </summary>
        public void OnDrawGizmos()
        {
            if (CurrentGrabber != null)
            {
                Gizmos.color = Color.green;
                Vector3 worldPos = CurrentGrabber.hand.AvatarHand.TransformPoint(LocalPositionOffset);
                Debug.Log($"Networked: {CurrentGrabber.hand.AvatarHand.position.ToString("F5")}");
                Gizmos.DrawSphere(worldPos, 0.05f);
            }
        }

        /// <summary>
        /// Client-side render update called for all clients.
        /// Triggers grab/ungrab events on grabber changes and handles visual extrapolation while waiting for authority.
        /// </summary>
        public override void Render()
        {
            // Check if the grabber changed, to trigger callbacks only (actual grabbing logic in handled in FUN for the state authority)
            // Those callbacks can't be called in FUN, as FUN is not called on proxies, while render is called for everybody
            if (TryDetectGrabberChange(_renderChangeDetector, out var previousGrabber, out var currentGrabber))
            {
                if (previousGrabber)
                {
                    if (onDidUngrab != null) onDidUngrab.Invoke();
                }
                if (currentGrabber)
                {
                    if (onDidGrab != null) onDidGrab.Invoke(currentGrabber);
                }
            }
            
            if (isTakingAuthority && extrapolateWhileTakingAuthority)
            {
                // If we are currently taking the authority on the object due to a grab, the network info are still not set
                //  but we will extrapolate anyway (if the option extrapolateWhileTakingAuthority is true) to avoid having the grabbed object staying still until we receive the authority
                ExtrapolateWhileTakingAuthority();
                return;
            }
            
            // No need to extrapolate if the object is not grabbed.
            // We do not extrapolate for proxies (might be relevant in some cases, but then the grabbing itself should be properly extrapolated, to avoid grabbing visually before the hand interpolation has reached the grabbing position)
            if (!IsGrabbed || Object.HasStateAuthority == false) return;
            
            // Extrapolation: Make visual representation follow grabber, adding position/rotation offsets
            var follwedGrabberRoot = CurrentGrabber.hand.AvatarHand != null ? CurrentGrabber.hand.AvatarHand.gameObject : CurrentGrabber.gameObject;
            grabbable.Follow(followedTransform: follwedGrabberRoot.transform, LocalPositionOffset, LocalRotationOffset);
        }
        
        #region Interface for local Grabbable (when the local user grab/ungrab this object)
        [SerializeField] bool deepDebug;
        
        /// <summary>
        /// Called locally when this object is ungrabbed by the local player.
        /// Resets the current grabber reference.
        /// </summary>
        public virtual void LocalUngrab()
        {
            if(deepDebug) Debug.LogError("NG.LocalUngrab");
            if (Object)
            {
                CurrentGrabber = null;
            }
        }
        
        /// <summary>
        /// Called locally to initiate a grab on this object.
        /// Requests state authority asynchronously and sets networked grab variables once authority is granted.
        /// </summary>
        public async virtual void LocalGrab()
        {
            // Ask and wait to receive the stateAuthority to move the object
            isTakingAuthority = true;
            await Object.WaitForStateAuthority();
            isTakingAuthority = false;

            // We waited to have the state authority before setting Networked vars
            LocalPositionOffset = grabbable.localPositionOffset;
            LocalRotationOffset = grabbable.localRotationOffset;

            if(grabbable.currentGrabber==null)
            {
                // The grabbable has already been ungrabbed
                if(deepDebug) Debug.LogError("The grabbable has already been ungrabbed");
                return;
            }
            // Update the CurrentGrabber in order to start following position in the FixedUpdateNetwork
            CurrentGrabber = grabbable.currentGrabber.networkGrabber;
        }
        #endregion
        
        /// <summary>
        /// Detects changes on the CurrentGrabber networked variable and returns previous and current values.
        /// </summary>
        /// <param name="changeDetector">ChangeDetector to use for detection.</param>
        /// <param name="previousGrabber">Output previous grabber.</param>
        /// <param name="currentGrabber">Output current grabber.</param>
        /// <returns>True if CurrentGrabber changed, otherwise false.</returns>
        private bool TryDetectGrabberChange(ChangeDetector changeDetector, out NetworkedGrabber previousGrabber, out NetworkedGrabber currentGrabber)
        {
            previousGrabber = null;
            currentGrabber = null;
            foreach (var changedNetworkedVarName in changeDetector.DetectChanges(this, out var previous, out var current))
            {
                if (changedNetworkedVarName == nameof(CurrentGrabber))
                {
                    var grabberReader = GetBehaviourReader<NetworkedGrabber>(changedNetworkedVarName);
                    previousGrabber = grabberReader.Read(previous);
                    currentGrabber = grabberReader.Read(current);
                    return true;
                }
            }
            return false;
        }
        
        /// <summary>
        /// Visually extrapolates the object's position and rotation based on the grabber while waiting for state authority transfer.
        /// </summary>
        protected virtual void ExtrapolateWhileTakingAuthority()
        {
            // No need to extrapolate if the object is not really grabbed
            if (grabbable.currentGrabber == null) return;
            NetworkedGrabber networkGrabber = grabbable.currentGrabber.networkGrabber;

            // Extrapolation: Make visual representation follow grabber, adding position/rotation offsets
            // We use grabberWhileTakingAuthority instead of CurrentGrabber as we are currently waiting for the authority transfer: the network vars are not already set, so we use the temporary versions
            var follwedGrabberRoot = networkGrabber.hand != null ? networkGrabber.hand.gameObject : networkGrabber.gameObject;
            grabbable.Follow(followedTransform: follwedGrabberRoot.transform, grabbable.localPositionOffset, grabbable.localRotationOffset);
        }
    }
}
