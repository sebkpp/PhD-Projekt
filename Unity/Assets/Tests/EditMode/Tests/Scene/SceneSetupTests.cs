using System.Reflection;
using NUnit.Framework;
using Application.Scripts.Scene;
using Application.Scripts.Avatar.Driver;
using Application.Scripts.Avatar;
using UnityEngine;

namespace Scene.Tests.EditMode
{
    public class SceneSetupTests
    {
        private GameObject _go;

        [SetUp]
        public void SetUp()
        {
            _go = new GameObject();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_go);
        }

        [Test]
        public void Awake_WhenAvatarDriverAndRigAssigned_CallsSetLocalRig()
        {
            var driverGo = new GameObject();
            var driver   = driverGo.AddComponent<AvatarDriver>();

            var rigGo = new GameObject();
            var rig   = rigGo.AddComponent<HardwareRig>();

            var setup = _go.AddComponent<SceneSetup>();
            typeof(SceneSetup)
                .GetField("_avatarDriver", BindingFlags.NonPublic | BindingFlags.Instance)
                .SetValue(setup, driver);
            typeof(SceneSetup)
                .GetField("_hardwareRig", BindingFlags.NonPublic | BindingFlags.Instance)
                .SetValue(setup, rig);

            // Invoke Awake manually
            typeof(SceneSetup)
                .GetMethod("Awake", BindingFlags.NonPublic | BindingFlags.Instance)
                .Invoke(setup, null);

            // Verify _localRig was set on driver
            var localRig = (HardwareRig)typeof(AvatarDriver)
                .GetField("_localRig", BindingFlags.NonPublic | BindingFlags.Instance)
                .GetValue(driver);

            Assert.AreEqual(rig, localRig);

            Object.DestroyImmediate(driverGo);
            Object.DestroyImmediate(rigGo);
        }

        [Test]
        public void Awake_WhenAvatarDriverIsNull_DoesNotThrow()
        {
            var setup = _go.AddComponent<SceneSetup>();
            // _avatarDriver left null — Awake must not throw
            Assert.DoesNotThrow(() =>
                typeof(SceneSetup)
                    .GetMethod("Awake", BindingFlags.NonPublic | BindingFlags.Instance)
                    .Invoke(setup, null)
            );
        }
    }
}
