using Application.Scripts.Feedback.Data;
using UnityEngine;

namespace Application.Scripts.Feedback.Auditory
{
    /// <summary>
    /// Generates a pure sine tone at the configured frequency.
    /// Volume scales continuously with grip strength: actualVolume = (config.volume/100) * grip.
    /// Uses OnAudioFilterRead for procedural audio — no AudioClip asset required.
    /// Attach to a GameObject with an AudioSource.
    /// </summary>
    [RequireComponent(typeof(AudioSource))]
    public class ToneAuditoryFeedback : MonoBehaviour, IAuditoryFeedbackProvider
    {
        private AudioSource _audioSource;
        private AuditoryStimulusData _config;
        private float _phase;
        private float _currentVolume;
        private bool _active;

        private void Awake()
        {
            _audioSource = GetComponent<AudioSource>();
            _audioSource.playOnAwake = false;
            _audioSource.loop = true;
            _audioSource.volume = 0f;
        }

        public void Activate(AuditoryStimulusData config)
        {
            _config = config;
            _phase = 0f;
            _currentVolume = 0f;
            _active = true;
            _audioSource.Play();
        }

        public void Deactivate()
        {
            _active = false;
            _audioSource.Stop();
            _currentVolume = 0f;
        }

        public void OnPhase(HandoverPhase phase) { }

        public void UpdateGrip(float ownGrip)
        {
            if (!_active || _config == null) return;
            _currentVolume = (_config.volume / 100f) * Mathf.Clamp01(ownGrip);
        }

        private void OnAudioFilterRead(float[] data, int channels)
        {
            if (!_active || _config == null) return;

            float frequency = _config.frequency;
            float sampleRate = AudioSettings.outputSampleRate;
            float phaseStep = 2f * Mathf.PI * frequency / sampleRate;

            for (int i = 0; i < data.Length; i += channels)
            {
                float sample = Mathf.Sin(_phase) * _currentVolume;
                for (int c = 0; c < channels; c++)
                    data[i + c] = sample;

                _phase += phaseStep;
                if (_phase > 2f * Mathf.PI)
                    _phase -= 2f * Mathf.PI;
            }
        }
    }
}
