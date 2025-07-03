using UnityEngine;

public class FingertrackerFollower : MonoBehaviour
{
    public Transform tragetFinger;

    void LateUpdate()
    {

        if (tragetFinger != null)
        {
            Debug.Log("sind");
            transform.position = tragetFinger.position;
            transform.rotation = tragetFinger.rotation;
        }
    }
}