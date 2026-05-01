using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Application.Scripts.Interaction
{
    public class ButtonEvents : MonoBehaviour
    {
        public void OnPress()
        {
            Debug.Log("SteamVR Button pressed!");
        }

        public void OnCustomButtonPress()
        {
            Debug.Log("We pushed our custom button!");
        }
    }
}
