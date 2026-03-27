namespace Application.Scripts.Utils.PID
{
    [System.Serializable]
    public struct PIDSettings
    {
        public float proportionalGain;
        public float integralGain;
        public float derivativeGain;
        public float maxIntegrationMagnitude;
    }
}