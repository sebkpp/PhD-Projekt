using System.Net.Configuration;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class TouchTrigger : MonoBehaviour
{
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            string mappedName = MapFingerName(gameObject.name);
            string msg = ExtractFingerID(mappedName) + "1";
            SendMessageToBLE(msg);
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("tangible"))
        {
            string mappedName = MapFingerName(gameObject.name);
            string msg = ExtractFingerID(mappedName) + "0";
            SendMessageToBLE(msg);
        }
    }

    string MapFingerName(string originalName)
    {
        switch (originalName)
        {
            case "ThumbC_R_end": return "Finger_5";
            case "IndexC_R_end": return "Finger_6";
            case "MiddleC_R_end": return "Finger_7";
            case "RingC_R_end": return "Finger_8";
            case "PinkyC_R_end": return "Finger_9";
            default: return originalName;
        }
    }

    string ExtractFingerID(string name)
    {
        return name.Substring(name.LastIndexOf('_') + 1);
    }

    void SendMessageToBLE(string message)
    {
        try
        {
            using (TcpClient client = new TcpClient("127.0.0.1", 5005))
            using (NetworkStream stream = client.GetStream())
            {
                byte[] data = Encoding.UTF8.GetBytes(message + "\n");
                stream.Write(data, 0, data.Length);
                Debug.Log("Nachricht an Python gesendet: " + message);
            }
        }
        catch (SocketException e)
        {
            Debug.Log("Verbindung zu Python fehlgeschlagen: " + e.Message);

        }
    }
}
