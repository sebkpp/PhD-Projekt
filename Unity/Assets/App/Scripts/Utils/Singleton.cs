using UnityEngine;

namespace Application.Scripts.Utils
{
    public class Singleton<T> : MonoBehaviour where T : Component
    {
        protected static T _instance;

        /// <summary>
        /// Singleton design pattern
        /// </summary>
        public static T Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindFirstObjectByType<T>();
                }
                return _instance;
            }
        }

        private void Awake()
        {
            // If there is an instance, and it's not me, delete myself.

            if (Instance != null && Instance != this)
            {
                Destroy(this);
            }
            else
            {
                _instance = this as T;
            }
        }

        // Prevent constructor use.
        protected Singleton() { }
    }
}
