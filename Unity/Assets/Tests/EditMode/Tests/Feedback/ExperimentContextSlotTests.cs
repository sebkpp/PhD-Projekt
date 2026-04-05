using NUnit.Framework;
using Application.Scripts.Network.Experiment;
using System.Reflection;
using System.Collections.Generic;

namespace Feedback.Tests.EditMode
{
    public class ExperimentContextSlotTests
    {
        private ExperimentContext CreateContextWithSlots(Dictionary<int, int> slotParticipant)
        {
            var go = new UnityEngine.GameObject();
            var ctx = go.AddComponent<ExperimentContext>();
            var field = typeof(ExperimentContext)
                .GetField("_slotParticipant", BindingFlags.NonPublic | BindingFlags.Instance);
            field.SetValue(ctx, slotParticipant);
            return ctx;
        }

        [Test]
        public void GetSlot_Player1_ReturnsSlot1()
        {
            var ctx = CreateContextWithSlots(new Dictionary<int, int> { { 1, 100 }, { 2, 200 } });
            Assert.AreEqual(1, ctx.GetSlot(1));
        }

        [Test]
        public void GetSlot_Player2_ReturnsSlot2()
        {
            var ctx = CreateContextWithSlots(new Dictionary<int, int> { { 1, 100 }, { 2, 200 } });
            Assert.AreEqual(2, ctx.GetSlot(2));
        }

        [Test]
        public void GetSlot_UnknownPlayer_ReturnsMinus1()
        {
            var ctx = CreateContextWithSlots(new Dictionary<int, int> { { 1, 100 } });
            Assert.AreEqual(-1, ctx.GetSlot(99));
        }
    }
}
