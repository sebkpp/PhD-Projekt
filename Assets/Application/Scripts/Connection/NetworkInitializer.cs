using Fusion;
using UnityEngine;

namespace Connection
{
    public class NetworkInitializer : MonoBehaviour
    {
        [SerializeField] private NetworkRunner runner;

        private void Awake()
        {
            if (runner == null)
                runner = FindObjectOfType<NetworkRunner>();

            runner.ProvideInput = true;
        }
    }
}