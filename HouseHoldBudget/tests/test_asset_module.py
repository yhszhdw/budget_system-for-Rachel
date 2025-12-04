import unittest
from budget_system.property.asset import Asset, PropertyRegistry


class TestAssetModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n[setUpClass] Asset tests start")

    @classmethod
    def tearDownClass(cls):
        print("[tearDownClass] Asset tests end\n")

    def setUp(self):
        self.registry = PropertyRegistry()

    def tearDown(self):
        print("[tearDown] Completed one Asset test")

    def test_create_and_add_asset(self):
        # Test asset creation and adding to registry
        a = Asset(
            name="House",
            asset_type="Real Estate",
            current_value=500000,
            owner="M001",
            date_acquired="2010-01-01"
        )
        self.assertEqual(a.name, "House")
        self.assertEqual(a.owner, "M001")
        self.assertGreater(a.current_value, 0)

        self.registry.add_asset(a)
        self.assertEqual(len(self.registry), 1)

        df = self.registry.to_dataframe()
        self.assertEqual(len(df), 1)
        self.assertIn("Asset ID", df.columns)

    def test_update_and_delete_asset(self):
        # Test updating and deleting asset
        a = Asset(
            name="Car",
            asset_type="Vehicle",
            current_value=20000,
            owner="M002",
            date_acquired="2018-01-01"
        )
        self.registry.add_asset(a)

        self.assertTrue(self.registry.update_asset_value(a.asset_id, 18000))
        self.assertEqual(a.current_value, 18000)

        self.assertTrue(self.registry.delete_asset(a.asset_id))
        self.assertEqual(len(self.registry), 0)

        # Delete non-existing asset
        self.assertFalse(self.registry.delete_asset("X000"))