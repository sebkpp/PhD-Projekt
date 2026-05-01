using NUnit.Framework;
using Application.Scripts.Feedback.Data;
using UnityEngine;

namespace Feedback.Tests.EditMode
{
    public class StimulusDataParsingTests
    {
        private const string SampleJson = @"[
          {
            ""slot"": 1,
            ""stimuli"": [
              {
                ""trial_slot_id"": 10,
                ""stimulus_id"": 2,
                ""stimulus"": {
                  ""stimulus_id"": 2,
                  ""name"": ""outer_hand"",
                  ""stimulus_type"": ""visual"",
                  ""visuals"": [""outer_hand""],
                  ""auditives"": [],
                  ""tactiles"": []
                }
              },
              {
                ""trial_slot_id"": 10,
                ""stimulus_id"": 6,
                ""stimulus"": {
                  ""stimulus_id"": 6,
                  ""name"": ""low_medium"",
                  ""stimulus_type"": ""auditory"",
                  ""visuals"": [],
                  ""auditives"": [{""frequency"": 50, ""volume"": 50}],
                  ""tactiles"": []
                }
              }
            ]
          },
          {
            ""slot"": 2,
            ""stimuli"": []
          }
        ]";

        [Test]
        public void ParseJson_TwoSlots_ReturnsBothSlots()
        {
            var result = StimulusSlotConfig.ParseArray(SampleJson);
            Assert.AreEqual(2, result.Length);
        }

        [Test]
        public void ParseJson_Slot1_HasTwoStimuli()
        {
            var result = StimulusSlotConfig.ParseArray(SampleJson);
            Assert.AreEqual(1, result[0].slot);
            Assert.AreEqual(2, result[0].stimuli.Length);
        }

        [Test]
        public void ParseJson_VisualStimulus_HasCorrectName()
        {
            var result = StimulusSlotConfig.ParseArray(SampleJson);
            var stimulus = result[0].stimuli[0];
            Assert.AreEqual("visual", stimulus.stimulus.stimulus_type);
            Assert.AreEqual("outer_hand", stimulus.stimulus.visuals[0]);
        }

        [Test]
        public void ParseJson_AudioStimulus_HasFrequencyAndVolume()
        {
            var result = StimulusSlotConfig.ParseArray(SampleJson);
            var audioStimulus = result[0].stimuli[1];
            Assert.AreEqual("auditory", audioStimulus.stimulus.stimulus_type);
            Assert.AreEqual(50, audioStimulus.stimulus.auditives[0].frequency);
            Assert.AreEqual(50, audioStimulus.stimulus.auditives[0].volume);
        }

        [Test]
        public void ParseJson_Slot2_HasEmptyStimuli()
        {
            var result = StimulusSlotConfig.ParseArray(SampleJson);
            Assert.AreEqual(2, result[1].slot);
            Assert.AreEqual(0, result[1].stimuli.Length);
        }

        [Test]
        public void GetVisualStimulusName_ReturnsFirstVisual()
        {
            var stimulus = new TrialSlotStimulusData
            {
                stimulus = new StimulusData
                {
                    stimulus_type = "visual",
                    visuals = new[] { "finger_color" }
                }
            };
            Assert.AreEqual("finger_color", stimulus.GetVisualName());
        }
    }
}
