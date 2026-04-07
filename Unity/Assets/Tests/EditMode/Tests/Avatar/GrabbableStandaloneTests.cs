using NUnit.Framework;
using Application.Scripts.InteractableObject;
using UnityEngine;

namespace Avatar.Tests.EditMode
{
    public class GrabbableStandaloneTests
    {
        private GameObject _go;
        private Grabbable  _grabbable;

        [SetUp]
        public void SetUp()
        {
            _go = new GameObject();
            _go.AddComponent<Rigidbody>();
            _grabbable = _go.AddComponent<Grabbable>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_go);
        }

        [Test]
        public void Grabbable_WithoutNetworkComponent_NetworkGrabbableIsNull()
        {
            Assert.IsNull(_grabbable.networkGrabbable);
        }

        [Test]
        public void LockObjectPhysics_SetsRigidbodyKinematic()
        {
            _go.GetComponent<Rigidbody>().isKinematic = false;

            _grabbable.LockObjectPhysics();

            Assert.IsTrue(_go.GetComponent<Rigidbody>().isKinematic);
        }

        [Test]
        public void UnlockObjectPhysics_RestoresExpectedKinematicState()
        {
            // Rigidbody defaults to non-kinematic; Awake captures that as expectedIsKinematic
            _go.GetComponent<Rigidbody>().isKinematic = false;
            // Re-run Awake logic: destroy and recreate so Awake fires after Rigidbody is non-kinematic
            Object.DestroyImmediate(_grabbable);
            _grabbable = _go.AddComponent<Grabbable>();

            _grabbable.LockObjectPhysics();
            _grabbable.UnlockObjectPhysics();

            Assert.IsFalse(_go.GetComponent<Rigidbody>().isKinematic);
        }

        [Test]
        public void OnGrab_Event_FiresOnInvoke()
        {
            bool fired = false;
            _grabbable.onGrab.AddListener(() => fired = true);

            _grabbable.onGrab.Invoke();

            Assert.IsTrue(fired);
        }
    }
}
