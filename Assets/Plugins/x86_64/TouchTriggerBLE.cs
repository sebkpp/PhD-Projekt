using UnityEngine;

public class TouchTriggerBLE : MonoBehaviour
{
    public BLEDevice bleDevice;

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            SendIntensity(true); // Motor ein
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            SendIntensity(false); // Motor aus
        }
    }

    void SendIntensity(bool entering)
    {
        string mappedName = MapFingerName(gameObject.name);
        int fingerID = int.Parse(ExtractFingerID(mappedName));
        int intensity = entering ? 255 : 0;
        string msg = $"Finger{fingerID}:{intensity}";
        bleDevice?.Send(msg);
        Debug.Log($"[TouchTriggerBLE] Finger {fingerID} → Intensität: {intensity}");
    }

    string MapFingerName(string originalName)
    {
        switch (originalName)
        {
            // Rechte Hand
            case "Tracker_ThumbC_R_end":  return "Finger_5";
            case "Tracker_IndexC_R_end":  return "Finger_6";
            case "Tracker_MiddleC_R_end": return "Finger_7";
            case "Tracker_RingC_R_end":   return "Finger_8";
            case "Tracker_PinkyC_R_end":  return "Finger_9";

            // Linke Hand
            case "Tracker_ThumbC_L_end":  return "Finger_0";
            case "Tracker_IndexC_L_end":  return "Finger_1";
            case "Tracker_MiddleC_L_end": return "Finger_2";
            case "Tracker_RingC_L_end":   return "Finger_3";
            case "Tracker_PinkyC_L_end":  return "Finger_4";

            default: return originalName;
        }
    }

    string ExtractFingerID(string name)
    {
        int underscoreIndex = name.LastIndexOf('_');
        return (underscoreIndex >= 0 && underscoreIndex < name.Length - 1)
            ? name.Substring(underscoreIndex + 1)
            : "X";
    }
}