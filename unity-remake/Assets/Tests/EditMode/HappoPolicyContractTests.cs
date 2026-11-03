using DongZhou.UnityRemake.Mobile;
using NUnit.Framework;

namespace DongZhou.UnityRemake.Tests
{
    public sealed class HappoPolicyContractTests
    {
        [Test]
        public void ValidInputPassesAndFallbackIsDeterministic()
        {
            var local = new float[HappoPolicyContract.LocalFeatureCount];
            var candidates = new float[HappoPolicyContract.CandidateFeatureCount * 3];
            var legal = new[] { false, true, true };

            Assert.That(HappoPolicyContract.Validate(local, candidates, legal, 2, out var reason), Is.True);
            Assert.That(reason, Is.EqualTo(HappoFallbackReason.None));
            Assert.That(HappoPolicyContract.FirstLegal(legal), Is.EqualTo(1));
        }

        [Test]
        public void NonFiniteFeatureIsRejected()
        {
            var local = new float[HappoPolicyContract.LocalFeatureCount];
            var candidates = new float[HappoPolicyContract.CandidateFeatureCount];
            var legal = new[] { true };
            candidates[7] = float.NaN;

            Assert.That(HappoPolicyContract.Validate(local, candidates, legal, 0, out var reason), Is.False);
            Assert.That(reason, Is.EqualTo(HappoFallbackReason.InvalidInput));
        }

        [Test]
        public void EmptyLegalSetIsRejectedWithoutInventingAnAction()
        {
            var local = new float[HappoPolicyContract.LocalFeatureCount];
            var candidates = new float[HappoPolicyContract.CandidateFeatureCount * 2];
            var legal = new[] { false, false };

            Assert.That(HappoPolicyContract.Validate(local, candidates, legal, 0, out var reason), Is.False);
            Assert.That(reason, Is.EqualTo(HappoFallbackReason.NoLegalAction));
            Assert.That(HappoPolicyContract.FirstLegal(legal), Is.EqualTo(-1));
        }
    }
}
