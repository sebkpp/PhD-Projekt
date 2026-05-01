using System.Collections;
using UnityEngine;

namespace Application.Scripts.Avatar
{
    public class Fader : MonoBehaviour
    {
        public bool FadedIn { get; private set; } //used by game manager and Network player

        [SerializeField] private float fadeSpeed = 0.1f;
        [SerializeField] private float transitionSpeed = 1f;

        private Material _material;
        private Color _color = Color.black;

        private void Start()
        {
            _material = GetComponent<MeshRenderer>().material;
            _color.a = 0f;
            _material.color = _color;
        }

        public void FadeTransition()
        {
            if (!gameObject.activeSelf) return;
            FadedIn = false;
            StartCoroutine(FadeTransitionCoroutine());
           
        }
        private IEnumerator FadeTransitionCoroutine()
        {
            //fade in
            while (_color.a < 1f)
            {
                _color.a += fadeSpeed * Time.deltaTime;
                _material.color = _color;
                yield return null;
            }

            //transition
            FadedIn = true;
            yield return new WaitForSeconds(transitionSpeed);

            //fade out
            while (_color.a > 0f)
            {
                _color.a -= fadeSpeed * Time.deltaTime;
                _material.color = _color;
                yield return null;
            }
            _color.a = 0f;
            _material.color = _color;
            
            //finished fading out
            FadedIn = false;
        }
    }
}