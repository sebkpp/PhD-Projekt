using System.Reflection;
using NUnit.Framework;
using Application.Scripts.Feedback.Auditory;
using Application.Scripts.Feedback.Data;
using UnityEngine;

namespace Feedback.Tests.EditMode
{
    public class ToneAuditoryFeedbackTests
    {
        private GameObject _go;
        private ToneAuditoryFeedback _sut;

        [SetUp]
        public void SetUp()
        {
            _go = new GameObject();
            _sut = _go.AddComponent<ToneAuditoryFeedback>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_go);
        }

        private static T GetField<T>(object obj, string name)
        {
            var field = obj.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance);
            return (T)field.GetValue(obj);
        }

        private static AuditoryStimulusData MakeConfig(int freq = 440, int vol = 80)
            => new AuditoryStimulusData { frequency = freq, volume = vol };

        [Test]
        public void Activate_SetsActiveTrue()
        {
            _sut.Activate(MakeConfig());
            Assert.IsTrue(GetField<bool>(_sut, "_active"));
        }

        [Test]
        public void Activate_StoresConfig()
        {
            var config = MakeConfig(freq: 220, vol: 60);
            _sut.Activate(config);
            var stored = GetField<AuditoryStimulusData>(_sut, "_config");
            Assert.AreEqual(220, stored.frequency);
            Assert.AreEqual(60, stored.volume);
        }

        [Test]
        public void Deactivate_SetsActiveFalse()
        {
            _sut.Activate(MakeConfig());
            _sut.Deactivate();
            Assert.IsFalse(GetField<bool>(_sut, "_active"));
        }

        [Test]
        public void Deactivate_ResetsVolume()
        {
            _sut.Activate(MakeConfig(vol: 100));
            _sut.UpdateGrip(1.0f);
            _sut.Deactivate();
            Assert.AreEqual(0f, GetField<float>(_sut, "_currentVolume"));
        }

        [Test]
        public void UpdateGrip_AfterActivate_SetsVolumeCorrectly()
        {
            _sut.Activate(MakeConfig(freq: 440, vol: 80));
            _sut.UpdateGrip(0.5f);
            float expected = (80f / 100f) * 0.5f;
            Assert.AreEqual(expected, GetField<float>(_sut, "_currentVolume"), 1e-5f);
        }

        [Test]
        public void UpdateGrip_FullVolume_IsScaledCorrectly()
        {
            _sut.Activate(MakeConfig(freq: 440, vol: 100));
            _sut.UpdateGrip(1.0f);
            Assert.AreEqual(1.0f, GetField<float>(_sut, "_currentVolume"), 1e-5f);
        }

        [Test]
        public void UpdateGrip_ZeroGrip_ResultsInZeroVolume()
        {
            _sut.Activate(MakeConfig(freq: 440, vol: 100));
            _sut.UpdateGrip(0f);
            Assert.AreEqual(0f, GetField<float>(_sut, "_currentVolume"), 1e-5f);
        }

        [Test]
        public void UpdateGrip_WhenInactive_DoesNotChangeVolume()
        {
            _sut.UpdateGrip(1.0f);
            Assert.AreEqual(0f, GetField<float>(_sut, "_currentVolume"));
        }

        [Test]
        public void UpdateGrip_GripAboveOne_IsClampedToOne()
        {
            _sut.Activate(MakeConfig(freq: 440, vol: 100));
            _sut.UpdateGrip(2.0f);
            Assert.LessOrEqual(GetField<float>(_sut, "_currentVolume"), 1.0f);
        }
    }
}
