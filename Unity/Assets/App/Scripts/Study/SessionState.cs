using System.Collections.Generic;
using Application.Scripts.Feedback.Data;

namespace Application.Scripts.Study
{
    public class SlotData
    {
        public int                SlotIndex     { get; }
        public string             Gender        { get; }
        public int                ParticipantId { get; }
        public StimulusSlotConfig Stimuli       { get; }

        public SlotData(int slotIndex, string gender, int participantId, StimulusSlotConfig stimuli)
        {
            SlotIndex     = slotIndex;
            Gender        = gender;
            ParticipantId = participantId;
            Stimuli       = stimuli;
        }
    }

    /// <summary>
    /// Immutable runtime snapshot of the active trial session.
    /// Populated by BackendService and distributed via OnSessionReady event.
    /// Key is playerId (Fusion PlayerId == slot index in Shared Mode).
    /// </summary>
    public class SessionState
    {
        public int TrialId      { get; }
        public int ExperimentId { get; }

        private readonly Dictionary<int, SlotData> _slots;

        public SessionState(int trialId, int experimentId, Dictionary<int, SlotData> slots)
        {
            TrialId      = trialId;
            ExperimentId = experimentId;
            _slots       = slots ?? new Dictionary<int, SlotData>();
        }

        /// <summary>Returns the slot index for the given Fusion PlayerId, or -1 if unknown.</summary>
        public int GetSlot(int playerId)
            => _slots.TryGetValue(playerId, out var s) ? s.SlotIndex : -1;

        /// <summary>Returns the gender string for the given Fusion PlayerId, or "Female" if unknown.</summary>
        public string GetGender(int playerId)
            => _slots.TryGetValue(playerId, out var s) ? s.Gender : "Female";

        /// <summary>Returns the participant DB-ID for the given Fusion PlayerId, or -1 if unknown.</summary>
        public int GetParticipantId(int playerId)
            => _slots.TryGetValue(playerId, out var s) ? s.ParticipantId : -1;

        /// <summary>Returns the stimulus config for the given slot index, or null if not loaded.</summary>
        public StimulusSlotConfig GetStimuli(int slot)
        {
            _slots.TryGetValue(slot, out var s);
            return s?.Stimuli;
        }
    }
}
