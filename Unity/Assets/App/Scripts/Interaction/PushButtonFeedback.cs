using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Application.Scripts.Interaction
{
    public class PushButtonFeedback : MonoBehaviour
    {
        [SerializeField] private AudioSource source;

        public void PlaySound()
        {
            if (!source)
            {
                Debug.LogWarning("Audiosource missing!");
                return;
            }
            source.Play();
        }
    }
}
