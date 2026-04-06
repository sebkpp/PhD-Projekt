using System.Collections.Generic;
using System.Reflection;
using NUnit.Framework;
using Application.Scripts.Study;
using UnityEngine;

namespace Study.Tests.EditMode
{
    public class BackendServiceOfflineTests
    {
        private GameObject    _go;
        private BackendService _sut;

        [SetUp]
        public void SetUp()
        {
            _go  = new GameObject();
            _sut = _go.AddComponent<BackendService>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_go);
        }

        private static StudySessionConfig MakeOfflineConfig(params (int trialId, int playerId, string gender)[] slots)
        {
            var config           = ScriptableObject.CreateInstance<StudySessionConfig>();
            config.offlineMode   = true;
            config.trials        = new TrialConfig[1];
            var trial            = new TrialConfig { trialId = slots[0].trialId };
            var slotList         = new SlotConfig[slots.Length];
            for (int i = 0; i < slots.Length; i++)
                slotList[i] = new SlotConfig { playerId = slots[i].playerId, gender = slots[i].gender, participantId = i + 1 };
            trial.slots    = slotList;
            config.trials[0] = trial;
            return config;
        }

        private static StudySessionConfig MakeMultiTrialConfig(int trialCount)
        {
            var config         = ScriptableObject.CreateInstance<StudySessionConfig>();
            config.offlineMode = true;
            config.trials      = new TrialConfig[trialCount];
            for (int i = 0; i < trialCount; i++)
                config.trials[i] = new TrialConfig { trialId = i + 1, slots = new SlotConfig[0] };
            return config;
        }

        private void InjectConfigAndStart(StudySessionConfig config)
        {
            typeof(BackendService)
                .GetField("_config", BindingFlags.NonPublic | BindingFlags.Instance)
                .SetValue(_sut, config);
            typeof(BackendService)
                .GetMethod("Start", BindingFlags.NonPublic | BindingFlags.Instance)
                .Invoke(_sut, null);
        }

        [Test]
        public void OfflineMode_OnSessionReady_IsFired()
        {
            var config  = MakeOfflineConfig((1, 1, "Male"));
            SessionState received = null;
            _sut.OnSessionReady.AddListener(s => received = s);

            InjectConfigAndStart(config);

            Assert.IsNotNull(received);
        }

        [Test]
        public void OfflineMode_SessionState_HasCorrectTrialId()
        {
            var config = MakeOfflineConfig((7, 1, "Male"));
            SessionState received = null;
            _sut.OnSessionReady.AddListener(s => received = s);

            InjectConfigAndStart(config);

            Assert.AreEqual(7, received.TrialId);
        }

        [Test]
        public void OfflineMode_SessionState_HasCorrectGender()
        {
            var config = MakeOfflineConfig((1, 1, "Female"));
            SessionState received = null;
            _sut.OnSessionReady.AddListener(s => received = s);

            InjectConfigAndStart(config);

            Assert.AreEqual("Female", received.GetGender(1));
        }

        [Test]
        public void OfflineMode_NoTrials_DoesNotFireOnSessionReady()
        {
            var config         = ScriptableObject.CreateInstance<StudySessionConfig>();
            config.offlineMode = true;
            config.trials      = new TrialConfig[0];

            bool fired = false;
            _sut.OnSessionReady.AddListener(_ => fired = true);

            InjectConfigAndStart(config);

            Assert.IsFalse(fired);
        }

        [Test]
        public void AdvanceToNextTrial_OfflineMode_FiresNextTrial()
        {
            var config = MakeMultiTrialConfig(2);
            var received = new List<SessionState>();
            _sut.OnSessionReady.AddListener(s => received.Add(s));

            InjectConfigAndStart(config);
            _sut.AdvanceToNextTrial();

            Assert.AreEqual(2, received.Count);
            Assert.AreEqual(2, received[1].TrialId);
        }

        [Test]
        public void AdvanceToNextTrial_LastTrial_FiresOnStudyComplete()
        {
            var config   = MakeMultiTrialConfig(1);
            bool completed = false;
            _sut.OnStudyComplete.AddListener(() => completed = true);

            InjectConfigAndStart(config);
            _sut.AdvanceToNextTrial();

            Assert.IsTrue(completed);
        }
    }
}
