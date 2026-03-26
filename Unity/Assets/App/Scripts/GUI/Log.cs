using UnityEngine.UI;
using TMPro;
using UnityEngine;
using System.Text;
using System;

namespace Application.Scripts.GUI
{
    public class Log : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI logAreaText;
        [SerializeField] private Button logAreaButton;
        [SerializeField] private bool hideOnStart = true;

        private readonly StringBuilder _log = new();
        private GameObject _logAreaParent;
        private TextMeshProUGUI _logAreaButtonText;

        private void OnEnable()
        {
            //Events
            logAreaButton.onClick.AddListener(LogDisplay);

            //References
            _logAreaParent = logAreaText.transform.parent.gameObject;
            _logAreaButtonText = logAreaButton.GetComponentInChildren<TextMeshProUGUI>();

            if (hideOnStart) LogDisplay();
        }
        private void LogDisplay()
        {
            _logAreaParent.SetActive(!_logAreaParent.activeSelf);
            _logAreaButtonText.text = !_logAreaParent.activeSelf ? "Show log" : "Hide log";
        }

        public void LogMessage(string message)
        {
            message += "\n";
            _log.Insert(0, message);
            logAreaText.text = _log.ToString();
        }
    }
}