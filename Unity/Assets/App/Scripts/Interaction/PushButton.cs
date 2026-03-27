using UnityEngine;
using UnityEngine.Events;

namespace Application.Scripts.Interaction
{
    public class PushButton : MonoBehaviour
    {
        [System.Serializable]
        public class ButtonEvent : UnityEvent { }

        public float pressLength;
        public bool pressed;
        public ButtonEvent downEvent;
        public ButtonEvent upEvent;

        Vector3 startPos;

        void Start()
        {
            startPos = transform.position;
        }

        void Update()
        {
            // If our distance is greater than what we specified as a press
            // set it to our max distance and register a press if we haven't already
            float distance = Mathf.Abs(transform.position.y - startPos.y);
            if (distance >= pressLength)
            {
                // Prevent the button from going past the pressLength
                transform.position = new Vector3(transform.position.x, startPos.y - pressLength, transform.position.z);
                if (!pressed)
                {
                    pressed = true;
                    // If we have an event, invoke it
                    downEvent?.Invoke();
                }
            } else
            {
                if (pressed && distance <= pressLength * 0.5f)
                {
                    pressed = false;
                    upEvent?.Invoke();
                }
                // If we aren't all the way down, reset our press
            }
            // Prevent button from springing back up past its original position
            if (transform.position.y > startPos.y)
            {
                transform.position = new Vector3(transform.position.x, startPos.y, transform.position.z);
            }
        }
    }
}
