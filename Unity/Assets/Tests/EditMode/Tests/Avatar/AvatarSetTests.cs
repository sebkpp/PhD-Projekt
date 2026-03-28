using NUnit.Framework;
using UnityEngine;
using Application.Scripts.Avatar.Visuals;

namespace Avatar.Tests.EditMode
{
    public class AvatarSetTests
    {
        [Test]
        public void GetPrefab_MaleGender_ReturnsMalePrefab()
        {
            var set = ScriptableObject.CreateInstance<AvatarSet>();
            var malePrefab   = new GameObject("Male");
            var femalePrefab = new GameObject("Female");
            set.malePrefab   = malePrefab;
            set.femalePrefab = femalePrefab;

            Assert.That(set.GetPrefab("Male"),   Is.SameAs(malePrefab));
            Assert.That(set.GetPrefab("Female"), Is.SameAs(femalePrefab));

            Object.DestroyImmediate(malePrefab);
            Object.DestroyImmediate(femalePrefab);
        }

        [Test]
        public void GetPrefab_UnknownGender_ReturnsFemale()
        {
            var set = ScriptableObject.CreateInstance<AvatarSet>();
            var femalePrefab = new GameObject("Female");
            set.femalePrefab = femalePrefab;

            Assert.That(set.GetPrefab("Diverse"), Is.SameAs(femalePrefab));

            Object.DestroyImmediate(femalePrefab);
        }
    }
}
