using System.Reflection;
using NUnit.Framework;
using Application.Scripts.Feedback.Visual;
using UnityEngine;

namespace Feedback.Tests.EditMode
{
    public class HandRenderingControllerTests
    {
        private GameObject _go;
        private HandRenderingController _sut;

        [SetUp]
        public void SetUp()
        {
            _go = new GameObject();
            _sut = _go.AddComponent<HandRenderingController>();
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

        [Test]
        public void PlayerId_WithoutNetworkRig_ReturnsMinus1()
        {
            Assert.AreEqual(-1, _sut.PlayerId);
        }

        [Test]
        public void SetMode_Left_StoresMode()
        {
            _sut.SetMode(HandRenderingMode.OH, null, isLeft: true);
            Assert.AreEqual(HandRenderingMode.OH, GetField<HandRenderingMode>(_sut, "_leftMode"));
        }

        [Test]
        public void SetMode_Right_StoresMode()
        {
            _sut.SetMode(HandRenderingMode.OH, null, isLeft: false);
            Assert.AreEqual(HandRenderingMode.OH, GetField<HandRenderingMode>(_sut, "_rightMode"));
        }

        [Test]
        public void SetMode_Left_StoresCollider()
        {
            var colliderGo = new GameObject();
            var collider = colliderGo.AddComponent<BoxCollider>();

            _sut.SetMode(HandRenderingMode.OH, collider, isLeft: true);

            Assert.AreEqual(collider, GetField<Collider>(_sut, "_leftHeldCollider"));
            Object.DestroyImmediate(colliderGo);
        }

        [Test]
        public void SetMode_Right_StoresCollider()
        {
            var colliderGo = new GameObject();
            var collider = colliderGo.AddComponent<BoxCollider>();

            _sut.SetMode(HandRenderingMode.OH, collider, isLeft: false);

            Assert.AreEqual(collider, GetField<Collider>(_sut, "_rightHeldCollider"));
            Object.DestroyImmediate(colliderGo);
        }

        [Test]
        public void SetMode_ClearCollider_SetsNull()
        {
            var colliderGo = new GameObject();
            var collider = colliderGo.AddComponent<BoxCollider>();
            _sut.SetMode(HandRenderingMode.OH, collider, isLeft: true);

            _sut.SetMode(HandRenderingMode.IH, null, isLeft: true);

            Assert.IsNull(GetField<Collider>(_sut, "_leftHeldCollider"));
            Object.DestroyImmediate(colliderGo);
        }

        [Test]
        public void SetMode_LeftDoesNotAffectRight()
        {
            _sut.SetMode(HandRenderingMode.OH, null, isLeft: true);
            Assert.AreEqual(HandRenderingMode.IH, GetField<HandRenderingMode>(_sut, "_rightMode"));
        }

        [Test]
        public void SetMode_RightDoesNotAffectLeft()
        {
            _sut.SetMode(HandRenderingMode.OH, null, isLeft: false);
            Assert.AreEqual(HandRenderingMode.IH, GetField<HandRenderingMode>(_sut, "_leftMode"));
        }

        [Test]
        public void DefaultModes_AreBothIH()
        {
            Assert.AreEqual(HandRenderingMode.IH, GetField<HandRenderingMode>(_sut, "_leftMode"));
            Assert.AreEqual(HandRenderingMode.IH, GetField<HandRenderingMode>(_sut, "_rightMode"));
        }
    }
}
