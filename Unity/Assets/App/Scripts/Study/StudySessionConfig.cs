using System;
using UnityEngine;

namespace Application.Scripts.Study
{
    /// <summary>
    /// Project asset that configures the study session.
    /// backendUrl and offlineMode control whether BackendService fetches from HTTP or uses trials[].
    /// Multiple assets can be created for different test scenarios (grab test, stimuli test, full flow).
    /// Menu: Assets → Create → ManualStudy → StudySessionConfig
    /// </summary>
    [CreateAssetMenu(menuName = "ManualStudy/StudySessionConfig", fileName = "Session_Default")]
    public class StudySessionConfig : ScriptableObject
    {
        [Header("Backend")]
        public string backendUrl          = "http://localhost:5000";
        public float  pollIntervalSeconds = 2f;

        [Header("Offline / Testing")]
        public bool offlineMode         = false;
        public bool logHandoversLocally = false;

        [Header("Offline Trial Sequence")]
        [Tooltip("Used when offlineMode = true. Served sequentially by BackendService.AdvanceToNextTrial().")]
        public TrialConfig[] trials = new TrialConfig[0];
    }

    [Serializable]
    public class TrialConfig
    {
        public int          trialId = 1;
        public SlotConfig[] slots   = new SlotConfig[0];
    }

    [Serializable]
    public class SlotConfig
    {
        [Tooltip("Fusion PlayerId (== slot index in Shared Mode)")]
        public int    playerId      = 1;
        public string gender        = "Male";
        public int    participantId = 1;

        [Header("Visual Stimulus")]
        [Tooltip("Name of a StimulusDefinition asset under Resources/Stimuli/ (e.g. outer_hand). Leave empty for no visual stimulus.")]
        public string visualStimulusName = "inner_hand";

        [Header("Auditory Stimulus")]
        public bool hasAuditoryStimulus = false;
        [Tooltip("Sine frequency in Hz")]
        public int  auditoryFrequency   = 440;
        [Tooltip("Volume 0-100")]
        public int  auditoryVolume      = 50;
    }
}
