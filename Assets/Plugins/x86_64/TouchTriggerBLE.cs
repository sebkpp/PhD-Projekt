using UnityEngine;

public class TouchTriggerBLE : MonoBehaviour
{
    public BLEDevice bleDevice;

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            string mappedName = MapFingerName(gameObject.name);
            string msg = "Finger" + ExtractFingerID(mappedName) + "on";
            bleDevice?.Send(msg);
            Debug.Log($"[??] Berührung erkannt ? {msg}");
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            string mappedName = MapFingerName(gameObject.name);
            string msg = "Finger" + ExtractFingerID(mappedName) + "off";
            bleDevice?.Send(msg);
            Debug.Log($"[?] Berührung gelöst ? {msg}");
        }
    }

    string MapFingerName(string originalName)
    {
        switch (originalName)
        {
            // Rechte Hand
            case "ThumbC_R_end": return "Finger_5";
            case "IndexC_R_end": return "Finger_6";
            case "MiddleC_R_end": return "Finger_7";
            case "RingC_R_end": return "Finger_8";
            case "PinkyC_R_end": return "Finger_9";

            // Linke Hand
            case "ThumbC_L_end": return "Finger_0";
            case "IndexC_L_end": return "Finger_1";
            case "MiddleC_L_end": return "Finger_2";
            case "RingC_L_end": return "Finger_3";
            case "PinkyC_L_end": return "Finger_4";

            default: return originalName;
        }
        }
    string ExtractFingerID(string name)
    {
        // Extrahiert die Zahl hinter dem letzten Unterstrich
        int underscoreIndex = name.LastIndexOf('_');
        return (underscoreIndex >= 0 && underscoreIndex < name.Length - 1)
                ? name.Substring(underscoreIndex + 1)
                : "X";
    }


}

