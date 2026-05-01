using System;
using UnityEngine;

namespace Application.Scripts.Feedback.Data
{
    [Serializable]
    public class AuditoryStimulusData
    {
        public int frequency;
        public int volume;
    }

    [Serializable]
    public class TactileStimulusData
    {
        public string pattern;
        public int intensity;
    }

    [Serializable]
    public class StimulusData
    {
        public int stimulus_id;
        public string name;
        public string stimulus_type;   // "visual" | "auditory" | "tactile"
        public string[] visuals;       // stimulus_name strings e.g. ["outer_hand"]
        public AuditoryStimulusData[] auditives;
        public TactileStimulusData[] tactiles;
    }

    [Serializable]
    public class TrialSlotStimulusData
    {
        public int trial_slot_id;
        public int stimulus_id;
        public StimulusData stimulus;

        /// <summary>Returns the visual stimulus name (e.g. "outer_hand") or null.</summary>
        public string GetVisualName()
        {
            if (stimulus == null || stimulus.visuals == null || stimulus.visuals.Length == 0)
                return null;
            return stimulus.visuals[0];
        }
    }

    [Serializable]
    public class StimulusSlotConfig
    {
        public int slot;
        public TrialSlotStimulusData[] stimuli;

        // JsonUtility wrapper for root-array deserialization
        [Serializable]
        private class Wrapper { public StimulusSlotConfig[] items; }

        /// <summary>
        /// Deserializes a JSON array of StimulusSlotConfig from the /trials/{id}/stimuli response.
        /// Uses a wrapper object because JsonUtility cannot deserialize root arrays.
        /// </summary>
        public static StimulusSlotConfig[] ParseArray(string json)
        {
            string wrapped = $"{{\"items\":{json}}}";
            var wrapper = JsonUtility.FromJson<Wrapper>(wrapped);
            return wrapper?.items ?? Array.Empty<StimulusSlotConfig>();
        }
    }
}
