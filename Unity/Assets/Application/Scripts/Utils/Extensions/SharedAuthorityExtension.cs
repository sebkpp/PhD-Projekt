using System.Threading.Tasks;
using Fusion;
using UnityEngine;

namespace Application.Scripts.Utils.Extensions
{
    public static class SharedAuthorityExtension
    {
        /**
         * Request state authority and wait for it to be received
         * Relevant in shared topology only
         */
        public static async Task<bool> WaitForStateAuthority(this NetworkObject o, float maxWaitTime = 8, bool request = true)
        {
            if (o == null)
            {
                Debug.LogError("Null network object");
                return false;
            }
            if (o.HasStateAuthority)
            {
                return true;
            }

            float waitStartTime = Time.time;
            if (request)
            {
                o.RequestStateAuthority();
            }
            while (!o.HasStateAuthority && (Time.time - waitStartTime) < maxWaitTime)
            {
                await Task.Delay(1);
            }
            return o.HasStateAuthority;
        }
    }
}