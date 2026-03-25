using System.Collections.Generic;
using Application.Scripts.Utils.Extensions;
using Interaction.Grasp;
using Application.Scripts.Network.Grasp;
using UnityEngine;

public class GraspableObject : MonoBehaviour
{
    [SerializeField] private List<GrabHand> _grabbers = new();

    public GrabHand currentGrabber;
    private GrabHand _previousGrabber;

    [SerializeField] public NetworkedGraspable networkGrabbable = null;

    public Vector3 localPositionOffset;
    public Quaternion localRotationOffset;
    public bool isGrabbed = false;
    
    private Rigidbody _rb;
    private bool isCollidingOffline = false;

    public Vector3 Velocity => _rb.linearVelocity;
    public Vector3 AngularVelocity => _rb.angularVelocity;

    public Rigidbody Rigidbody => _rb;

    public bool IsGrabbed => currentGrabber != null;
    protected virtual void Awake()
    {
        networkGrabbable = GetComponent<NetworkedGraspable>();
        _rb = GetComponentInChildren<Rigidbody>();
        _rb.isKinematic = false;
    }

    #region Follow configuration

    [Header("Follow configuration")] [Range(0, 1)]
    public float followVelocityAttenuation = 0.5f;

    public float maxVelocity = 10f;
    
    #endregion
    
    public virtual bool Grab(GrabHand newGrabber)
    {
        if (_grabbers.Contains(newGrabber))
            return false;
        
        //if (isGrabbed) return false;
        
        _grabbers.Add(newGrabber);
        isGrabbed = true;
        _rb.useGravity = false;
        
        Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> Object {gameObject.name} got grasped.");
        if (_grabbers.Count == 1)
        {
            // First grabber
            currentGrabber = newGrabber;
            // Find grabbable position/rotation in grabber referential
            localPositionOffset = newGrabber.transform.InverseTransformPoint(transform.position);
            localRotationOffset = Quaternion.Inverse(newGrabber.transform.rotation) * transform.rotation; 

            // Handle input authority for the first grabber
            //HandleInputAuthority(currentGrabber, true);
        }
        else
        {
            // Second grabber
            _previousGrabber = currentGrabber;
            currentGrabber = newGrabber;

            // Evaluate grasp strengths
            // EvaluateGraspStrengths();
        }

        return true;
    }

    public virtual void Ungrab(GrabHand grabber)
    {
        if (_grabbers.Contains(grabber))
        {
            _grabbers.Remove(grabber);
            if (_grabbers.Count == 0)
            {
                isGrabbed = false;
                _rb.useGravity = true;
                currentGrabber = null;
                Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> Object {gameObject.name} released by {grabber.name}.");
            }
            else if (currentGrabber == grabber)
            {
                // Transfer authority to remaining grabber
                currentGrabber = _grabbers[0];
                //HandleInputAuthority(currentGrabber, true);
            }
        }
        
        //currentGrabber = null;
        //isGrabbed = false;
        //_rb.useGravity = true;
        
        //Debug.Log($"<color=#ADD8E6>[Grasp:Local]</color> Object {gameObject.name} got released. ");
    }
    
    #region Following logic

    public virtual void Follow(Transform followedTransform, float elapsedTime)
    {
        VelocityFollow(followedTransform, elapsedTime);
    }

    public virtual void VelocityFollow(Transform followedTransform, float elapsedTime)
    {
        // Compute the requested velocity to joined target position during a Runner.DeltaTime
        _rb.VelocityFollow(target: followedTransform, localPositionOffset, localRotationOffset, elapsedTime);

        // To avoid a too aggressive move, we attenuate and limit a bit the expected velocity
        var velocity = _rb.linearVelocity;
        velocity *= followVelocityAttenuation; // followVelocityAttenuation = 0.5F by default
        _rb.linearVelocity = velocity;
        _rb.linearVelocity = Vector3.ClampMagnitude(velocity, maxVelocity); // maxVelocity = 10f by default
    }

    #endregion

    private void FixedUpdate()
    {
        // We handle the following if we are not online (in that case, the Follow will be called by the NetworkGrabbable during FUN and Render)
        if (networkGrabbable == null || networkGrabbable.Object == null)
        {
            // Note that this offline following will not offer the pseudo-haptic feedback (it could easily be recreated offline if needed)
            if (IsGrabbed)
                Follow(followedTransform: currentGrabber.transform, Time.fixedDeltaTime);
        }
    
        isCollidingOffline = false;
    }

    private void OnCollisionStay(Collision collision)
    {
        isCollidingOffline = true;
    }
}