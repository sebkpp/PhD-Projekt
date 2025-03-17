using Fusion;
using UnityEngine;
using UnityEngine.SceneManagement;

[System.Serializable]
public class VRMap
{
    public Transform vrTarget;
    public Transform ikTarget;
    public Vector3 trackingPositionOffset;
    public Vector3 trackingRotationOffset;
    public void Map()
    {
        ikTarget.position = vrTarget.TransformPoint(trackingPositionOffset);
        ikTarget.rotation = vrTarget.rotation * Quaternion.Euler(trackingRotationOffset);
    }
    
}

[System.Serializable]
public class VRFingerMap
{
    public Transform vrTarget;
    public Transform ikTarget;
    public Vector3 trackingPositionOffset;
    public Vector3 trackingRotationOffset;
    public void Map()
    {
        ikTarget.position = vrTarget.TransformPoint(trackingPositionOffset);
        ikTarget.rotation = vrTarget.rotation * Quaternion.Euler(trackingRotationOffset);
    }
}

public class IKTargetFollowVRRig : MonoBehaviour
{
    [Range(0,1)]
    public float turnSmoothness = 0.1f;
    public VRMap head;
    public VRMap leftHand;
    public VRMap rightHand;
    public VRFingerMap[] leftHandFingers;
    public VRFingerMap[] rightHandFingers;

    public Vector3 headBodyPositionOffset;
    public float headBodyYawOffset;



    void Start()
    {
        GameObject targetHead = GameObject.FindWithTag("HeadVrTarget");
        GameObject targetLeftHand = GameObject.FindWithTag("LifthandVrTarget");
        GameObject targetRightHand = GameObject.FindWithTag("RighthandVrTarget");

        GameObject[] targetRightfinger = new GameObject[5];
        GameObject[] targetLeftfinger = new GameObject[5];

        bool allTargetsFound = true;

        if (targetHead == null)
        {
            Debug.LogWarning("HeadVrTarget not found in the active scene.");
            allTargetsFound = false;
        }
        if (targetLeftHand == null)
        {
            Debug.LogWarning("LeftHandVrTarget not found in the active scene.");
            allTargetsFound = false;
        }
        if (targetRightHand == null)
        {
            Debug.LogWarning("RightHandVrTarget not found in the active scene.");
            allTargetsFound = false;
        }

        for (int i = 0; i < 5; i++)
        {
            targetRightfinger[i] = GameObject.FindWithTag("RFVrTarget" + i);
            targetLeftfinger[i] = GameObject.FindWithTag("LFVrTarget" + i);

            if (targetRightfinger[i] == null)
            {
                Debug.LogWarning("RFVrTarget" + i + " not found in the active scene.");
                allTargetsFound = false;
            }
            if (targetLeftfinger[i] == null)
            {
                Debug.LogWarning("LFVrTarget" + i + " not found in the active scene.");
                allTargetsFound = false;
            }
        }

        if (allTargetsFound)
        {
            head.vrTarget = targetHead.transform;
            leftHand.vrTarget = targetLeftHand.transform;
            rightHand.vrTarget = targetRightHand.transform;

            for (int i = 0; i < 5; i++)
            {
                rightHandFingers[i].vrTarget = targetRightfinger[i].transform;
                leftHandFingers[i].vrTarget = targetLeftfinger[i].transform;
            }
        }
        else
        {
            Debug.LogWarning("Object with the specified tag not found in the active scene.");
        }
    }


    void LateUpdate()
    {
        
        if (head.vrTarget != null)
            
        {
            
        
         transform.position = head.ikTarget.position + headBodyPositionOffset;
         float yaw = head.vrTarget.eulerAngles.y;
        transform.rotation = Quaternion.Lerp(transform.rotation,Quaternion.Euler(transform.eulerAngles.x, yaw, transform.eulerAngles.z),turnSmoothness);

        head.Map();
        leftHand.Map();
        rightHand.Map();
        foreach (var finger in leftHandFingers)
        {
            finger.Map();
        }

        foreach (var finger in rightHandFingers)
        {
            finger.Map();
        }
        }
    }
}
