using NUnit.Framework;
using Application.Scripts.Study;
using Application.Scripts.Feedback.Data;
using System.Collections.Generic;

namespace Study.Tests.EditMode
{
    public class SessionStateTests
    {
        private SessionState BuildSession()
        {
            var stimuli = new StimulusSlotConfig { slot = 1, stimuli = new TrialSlotStimulusData[0] };
            var slots = new Dictionary<int, SlotData>
            {
                { 1, new SlotData(1, "Male",   101, stimuli) },
                { 2, new SlotData(2, "Female", 202, null)    }
            };
            return new SessionState(trialId: 5, experimentId: 3, slots: slots);
        }

        [Test]
        public void TrialId_ReturnsConstructorValue()
        {
            Assert.AreEqual(5, BuildSession().TrialId);
        }

        [Test]
        public void GetSlot_KnownPlayer_ReturnsSlotIndex()
        {
            Assert.AreEqual(1, BuildSession().GetSlot(1));
        }

        [Test]
        public void GetSlot_UnknownPlayer_ReturnsMinus1()
        {
            Assert.AreEqual(-1, BuildSession().GetSlot(99));
        }

        [Test]
        public void GetGender_KnownPlayer_ReturnsGender()
        {
            Assert.AreEqual("Male", BuildSession().GetGender(1));
        }

        [Test]
        public void GetGender_UnknownPlayer_ReturnsFemale()
        {
            Assert.AreEqual("Female", BuildSession().GetGender(99));
        }

        [Test]
        public void GetParticipantId_KnownPlayer_ReturnsId()
        {
            Assert.AreEqual(101, BuildSession().GetParticipantId(1));
        }

        [Test]
        public void GetParticipantId_UnknownPlayer_ReturnsMinus1()
        {
            Assert.AreEqual(-1, BuildSession().GetParticipantId(99));
        }

        [Test]
        public void GetStimuli_KnownSlot_ReturnsConfig()
        {
            Assert.IsNotNull(BuildSession().GetStimuli(1));
        }

        [Test]
        public void GetStimuli_NullStimuli_ReturnsNull()
        {
            Assert.IsNull(BuildSession().GetStimuli(2));
        }
    }
}
