using NUnit.Framework;
using UnityEngine;

namespace DongZhou.UnityRemake.Tests
{
    public sealed class DongJiaoRulesTests
    {
        [Test]
        public void TerrainContractMatchesNineteenByFourteenGrid()
        {
            Assert.AreEqual(14, DongJiaoRules.Terrain.Length);
            foreach (string row in DongJiaoRules.Terrain)
                Assert.AreEqual(19, row.Length);
        }

        [TestCase('r')]
        [TestCase('W')]
        [TestCase('~')]
        [TestCase('P')]
        public void StructuralTerrainIsImpassable(char terrain)
        {
            Assert.IsFalse(DongJiaoRules.IsPassable(terrain));
        }

        [Test]
        public void OriginalDeploymentsArePassable()
        {
            Assert.IsTrue(DongJiaoRules.IsPassable(2, 6));
            Assert.IsTrue(DongJiaoRules.IsPassable(2, 8));
            Assert.IsTrue(DongJiaoRules.IsPassable(16, 1));
        }

        [Test]
        public void MovementUsesOrthogonalDistance()
        {
            Assert.AreEqual(7, DongJiaoRules.Distance(new Vector2Int(2, 8), new Vector2Int(6, 11)));
        }
    }
}
