using UnityEngine;

namespace Application.Scripts.Utils.PID
{
    [System.Serializable]
    public struct PIDState
    {
        public PIDSettings pidSettings;
        public Vector3 errorIntegration;
        public Vector3 lastError;
        
        private Vector3 lastPosition;
        private bool derivateInitialized;

        // For explanation about PID controllers, see https://www.youtube.com/watch?v=y3K6FUgrgXw
        public Vector3 UpdateCommand(Vector3 error, float dt, bool ignoreIntegration = false)
        {
            // P
            var p = pidSettings.proportionalGain * error;

            // I
            var i = Vector3.zero;
            if (ignoreIntegration == false)
            {
                var newErrorIntegration = errorIntegration + dt * error;
                errorIntegration = Vector3.ClampMagnitude(newErrorIntegration, pidSettings.maxIntegrationMagnitude);
                i = pidSettings.integralGain * errorIntegration;
            }

            // D
            Vector3 d = Vector3.zero;
            if (derivateInitialized)
            {
                var errorDerivate = (error - lastError) / dt;
                d = pidSettings.derivativeGain * errorDerivate;
            }

            // Update for next controller update
            lastError = error;
            derivateInitialized = true;

            // Command
            return p + i + d;
        }

        public void Reset()
        {
            Debug.LogError("Reset");
            lastError = Vector3.zero;
            derivateInitialized = false;
            errorIntegration = Vector3.zero;
        }
    }
}