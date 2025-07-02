using System.Collections;
using System.Text;
using UnityEngine;

public class BLEDevice : MonoBehaviour
{
    [Header("Verbindungsmodus")]
    public bool useDirectUUIDs = false;
    public string directServiceUUID = "";
    public string directCharacteristicUUID = "";

    [Header("Geräteeinstellungen")]
    public string deviceName = "esp32_left";

    [Header("Debug & Verhalten")]
    public bool enableDebugLogging = true;
    public float serviceScanDelay = 2f;
    public bool retryIfNoServiceFound = true;
    public bool acceptAnyCharacteristic = true;

    [Header("Automatische Nachricht nach Verbindung")]
    public bool sendOnConnect = true;
    public string autoMessage = "Finger3on";

    private string deviceId = null;
    private string resolvedServiceUUID = null;
    private string resolvedCharacteristicUUID = null;
    private bool connected = false;

    void Start()
    {
        Log($"🔍 Suche nach Gerät: {deviceName}");
        BleApi.StartDeviceScan();
        StartCoroutine(ScanAndConnect());
    }

    IEnumerator ScanAndConnect()
    {
        for (int i = 0; i < 200; i++)
        {
            BleApi.DeviceUpdate update = new BleApi.DeviceUpdate();
            if (BleApi.PollDevice(ref update, false) == BleApi.ScanStatus.AVAILABLE &&
                update.name == deviceName)
            {
                deviceId = update.id;
                Log($"✅ Gerät gefunden: {deviceId}");
                BleApi.StopDeviceScan();
                yield return new WaitForSeconds(1f);
                break;
            }
            yield return new WaitForSeconds(0.05f);
        }

        if (deviceId == null)
        {
            LogError($"❌ Gerät nicht gefunden: {deviceName}");
            yield break;
        }

        if (useDirectUUIDs)
        {
            resolvedServiceUUID = directServiceUUID;
            resolvedCharacteristicUUID = directCharacteristicUUID;
            connected = true;
            Log($"🔗 Direkt verbunden → Service: {resolvedServiceUUID} → Characteristic: {resolvedCharacteristicUUID}");

            if (sendOnConnect && !string.IsNullOrEmpty(autoMessage))
                StartCoroutine(SendAutoMessage());

            yield break;
        }

        Log($"⏳ Warte {serviceScanDelay} Sekunden, bevor Services gescannt werden...");
        yield return new WaitForSeconds(serviceScanDelay);

        string[] services = new string[20];
        int serviceCount = 0;

        BleApi.ScanServices(deviceId);
        for (int i = 0; i < 100; i++)
        {
            if (BleApi.PollService(out BleApi.Service service, false) == BleApi.ScanStatus.AVAILABLE)
            {
                Log($"➡️ Service gefunden: {service.uuid}");
                if (IsCustomService(service.uuid) && serviceCount < services.Length)
                    services[serviceCount++] = service.uuid;
            }
            yield return null;
        }

        if (serviceCount == 0 && retryIfNoServiceFound)
        {
            LogWarning("🟡 Keine benutzerdefinierten Services – erneuter Versuch...");
            yield return new WaitForSeconds(2f);
            BleApi.ScanServices(deviceId);
            for (int i = 0; i < 100; i++)
            {
                if (BleApi.PollService(out BleApi.Service retryService, false) == BleApi.ScanStatus.AVAILABLE)
                {
                    Log($"➡️ (Retry) Service gefunden: {retryService.uuid}");
                    if (IsCustomService(retryService.uuid) && serviceCount < services.Length)
                        services[serviceCount++] = retryService.uuid;
                }
                yield return null;
            }
        }

        if (serviceCount == 0)
        {
            LogError("❌ Keine benutzerdefinierten Services gefunden.");
            yield break;
        }

        bool charFound = false;
        for (int s = 0; s < serviceCount; s++)
        {
            string svc = services[s];
            BleApi.ScanCharacteristics(deviceId, svc);
            for (int j = 0; j < 100; j++)
            {
                if (BleApi.PollCharacteristic(out BleApi.Characteristic c, false) == BleApi.ScanStatus.AVAILABLE)
                {
                    Log($"➡️ Characteristic gefunden: {c.uuid} unter Service {svc}");
                    if (!charFound && acceptAnyCharacteristic)
                    {
                        resolvedServiceUUID = svc;
                        resolvedCharacteristicUUID = c.uuid;
                        charFound = true;
                        LogWarning($"⚠️ Write-Properties nicht geprüft – sende trotzdem an: {c.uuid} unter {svc}");
                    }
                }
                yield return null;
            }
        }

        if (!charFound)
        {
            LogError("❌ Keine passende Characteristic gefunden.");
            yield break;
        }

        connected = true;
        Log($"🔗 Verbunden mit {deviceName} → Service: {resolvedServiceUUID} → Characteristic: {resolvedCharacteristicUUID}");

        if (sendOnConnect && !string.IsNullOrEmpty(autoMessage))
            StartCoroutine(SendAutoMessage());
    }

    IEnumerator SendAutoMessage()
    {
        yield return new WaitForSeconds(1f);
        Send(autoMessage);
    }

    public void Send(string message)
    {
        if (!connected)
        {
            LogError($"⚠️ Nicht verbunden – konnte '{message}' nicht senden.");
            return;
        }

        try
        {
            var buffer = Encoding.UTF8.GetBytes(message);
            var data = new BleApi.BLEData
            {
                buf = buffer,
                size = (short)buffer.Length,
                deviceId = deviceId,
                serviceUuid = resolvedServiceUUID,
                characteristicUuid = resolvedCharacteristicUUID
            };

            bool result = BleApi.SendData(in data, false);
            if (result)
                Log($"📤 Gesendet: '{message}' an {deviceName}");
            else
                LogError($"❌ Senden fehlgeschlagen → UUID: {resolvedCharacteristicUUID} | Größe: {data.size}");
        }
        catch (System.Exception ex)
        {
            LogError($"💥 Ausnahme beim Senden: {ex.Message}");
        }
    }

    public bool IsConnected => connected;

    private bool IsCustomService(string uuid)
    {
        return !uuid.StartsWith("000018");
    }

    private void Log(string msg)
    {
        if (enableDebugLogging)
            Debug.Log(msg);
    }

    private void LogError(string msg)
    {
        if (enableDebugLogging)
            Debug.LogError(msg);
    }

    private void LogWarning(string msg)
    {
        if (enableDebugLogging)
            Debug.LogWarning(msg);
    }
}
