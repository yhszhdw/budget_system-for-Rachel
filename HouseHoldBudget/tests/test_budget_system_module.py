import unittest
from unittest.mock import patch

import budget_system.budget_system as bs
from budget_system.budget_system import BudgetSystem
from budget_system.member.member_type import guardian, dependant


class TestBudgetSystemModule(unittest.TestCase):

    def setUp(self):
        # Fresh system for each test
        self.system = BudgetSystem(
            current_fund=1000,
            address="123 Test St",
            household_name="Test Family",
            members=[]
        )

    # ========= Core logic: members =========

    def test_add_get_remove_member_and_str(self):
        d = dependant("Child", "D1", "2015-01-01")
        self.assertTrue(self.system.add_member(d))
        self.assertEqual(len(self.system.members), 1)
        self.assertIsNotNone(self.system.get_member("D1"))
        self.assertIsNone(self.system.get_member("NO_SUCH"))

        # duplicate add
        self.assertFalse(self.system.add_member(d))

        # remove success
        self.assertTrue(self.system.remove_member("D1"))
        # remove fail
        self.assertFalse(self.system.remove_member("D1"))

        # __str__ basic check
        text = str(self.system)
        self.assertIn("Test Family", text)
        self.assertIn("123 Test St", text)

    def test_list_member_with_and_without_members(self):
        # just make sure no exception and both branches are hit
        self.system.list_member()  # no members

        d = dependant("Child", "D1", "2015-01-01")
        self.system.add_member(d)
        self.system.list_member()  # with members

    # ========= Core logic: fund =========

    def test_fund_add_sub_validate_get_df_and_summarize(self):
        self.system.add_fund(200, "Salary")
        self.system.sub_fund(50, "Snacks")
        df_all = self.system.get_df()
        self.assertGreaterEqual(len(df_all), 2)

        # get_df with start/end = None explicitly
        df_range = self.system.get_df(start=None, end=None)
        self.assertGreaterEqual(len(df_range), 2)

        # validate fund (True)
        self.assertTrue(self.system.validate_fund(1000))
        # validate fund (False, amount too large)
        self.assertFalse(self.system.validate_fund(999999999))

        # search & filter & summarize_month wrapper
        self.system.add_fund(300, "Income")
        self.system.sub_fund(80, "Groceries")

        res_search = self.system.search_fund_log("Income")
        self.assertIsNotNone(res_search)

        res_status_true = self.system.filter_fund_status(True)
        res_status_false = self.system.filter_fund_status(False)
        self.assertIsNotNone(res_status_true)
        self.assertIsNotNone(res_status_false)

        # summarize_month, both single-month and range path
        self.system.summarize_month("2025-01")
        self.system.summarize_month("2025-01", "2025-02")

        # visualize just to hit path
        self.system.visualize("2025-01")

    # ========= Core logic: upgrade_member =========

    def test_upgrade_member_not_found_and_already_guardian(self):
        # not found
        self.assertFalse(self.system.upgrade_member("NO_SUCH"))

        g = guardian("Parent", "G1", "1980-01-01", income=90000, job_title="Engineer")
        self.system.add_member(g)
        # already guardian
        self.assertFalse(self.system.upgrade_member("G1"))

    def test_upgrade_member_success(self):
        d = dependant("Child", "D1", "2015-01-01")
        self.system.add_member(d)

        inputs = ["Engineer", "80000"]
        with patch("budget_system.budget_system.input", side_effect=inputs):
            result = self.system.upgrade_member("D1")

        self.assertTrue(result)
        upgraded = self.system.get_member("D1")
        self.assertIsNotNone(upgraded)
        self.assertEqual(getattr(upgraded, "type", ""), "guardian")

    # ========= Core logic: assets & registry =========

    def test_add_asset_success_update_delete_summary_and_vis(self):
        g = guardian("Parent", "G1", "1980-01-01", income=90000, job_title="Engineer")
        self.system.add_member(g)

        asset = self.system.add_asset_for_member(
            member_id="G1",
            name="House",
            asset_type="Real Estate",
            current_value=500000,
            date_acquired="2020-01-01"
        )
        self.assertIsNotNone(asset)
        self.assertEqual(asset.owner, "G1")
        self.assertEqual(len(self.system.property_registry), 1)

        asset_id = asset.asset_id

        # update value
        self.assertTrue(self.system.update_asset_value(asset_id, 600000))
        # update non-existing asset
        self.assertFalse(self.system.update_asset_value("NO_SUCH", 123))

        # search assets with hit and miss
        df_hit = self.system.search_assets("House")
        self.assertIsNotNone(df_hit)
        self.assertGreater(len(df_hit), 0)

        df_miss = self.system.search_assets("NO_SUCH_NAME")
        self.assertIsNotNone(df_miss)

        # summary
        summary = self.system.summarize_assets()
        self.assertIn("Total Value", summary)
        self.assertGreaterEqual(summary["Total Value"], 0)

        # visualization by Type & Owner
        df_vis_type = self.system.get_asset_visualization_data(group_by="Type")
        df_vis_owner = self.system.get_asset_visualization_data(group_by="Owner")
        self.assertIsNotNone(df_vis_type)
        self.assertIsNotNone(df_vis_owner)

        # delete asset
        self.assertTrue(self.system.delete_asset(asset_id))
        # delete again
        self.assertFalse(self.system.delete_asset(asset_id))

    def test_add_asset_fails_when_member_not_found(self):
        result = self.system.add_asset_for_member(
            member_id="NO_SUCH",
            name="Car",
            asset_type="Vehicle",
            current_value=20000
        )
        self.assertIsNone(result := result)

    # ========= initialization =========

    def test_initialization_with_system_already_provided(self):
        with patch("budget_system.budget_system.main_menu") as mock_menu:
            sys2 = bs.initialization(system=self.system)
        self.assertIs(sys2, self.system)
        mock_menu.assert_called_once()

    def test_initialization_first_time_setup(self):
        side_effect = [
            "My Family",   # household_name
            "1500",        # balance
            "Test Address",# address
            ""             # final "press enter"
        ]
        with patch("budget_system.budget_system.input", side_effect=side_effect):
            sys2 = bs.initialization(system=None)

        self.assertIsInstance(sys2, BudgetSystem)
        self.assertEqual(sys2.household_name, "My Family")
        self.assertEqual(sys2.address, "Test Address")

    # ========= CLI: main_menu =========

    def test_main_menu_all_options(self):
        # 依次走 1,2,3,4,5 分支，每个子菜单函数直接被 fake 掉
        inputs = ["1", "2", "3", "4", "5"]
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.member_editor") as mock_member, \
             patch("budget_system.budget_system.fund_editor") as mock_fund, \
             patch("budget_system.budget_system.log_viewer") as mock_log, \
             patch("budget_system.budget_system.property_editor") as mock_prop, \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.main_menu(self.system)

        mock_member.assert_called_once()
        mock_fund.assert_called_once()
        mock_log.assert_called_once()
        mock_prop.assert_called_once()

    def test_main_menu_quick_quit(self):
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=["5"]):
            bs.main_menu(self.system)

    # ========= CLI: member_editor =========

    def test_member_editor_list_and_exit(self):
        d = dependant("Child", "D1", "2015-01-01")
        self.system.add_member(d)

        inputs = [
            "1",  # list
            "",   # press enter
            "6"   # exit
        ]
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.member_editor(self.system)

    def test_member_editor_add_delete_upgrade_edit_and_exit(self):
        # 一口气跑 2->3->4->5->6 这些分支
        inputs = [
            # 2. Add member (guardian)
            "2",                # menu choice
            "New Guardian",     # Name
            "1980-01-01",       # DOB
            "G99",              # ID
            "guardian",         # type
            "Engineer",         # Job Title
            "80000",            # Income
            "",                 # Press Enter to return...
            # 3. Delete member (ID not found, just走一下分支)
            "3",
            "NO_SUCH",
            "",
            # 4. Upgrade member (we stub upgrade_member)
            "4",
            "G99",
            "",
            # 5. Edit member by ID (stub member_edit)
            "5",
            "G99",
            "",
            # 6. Exit
            "6",
        ]
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch.object(self.system, "upgrade_member", return_value=True), \
             patch("budget_system.budget_system.member_edit") as mock_edit, \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.member_editor(self.system)

        mock_edit.assert_called()

    # ========= CLI: fund_editor =========

    def test_fund_editor_add_sub_and_back(self):
        inputs = [
            # 1. Add Fund
            "1",
            "100",
            "Salary",
            "2025-01-01",
            "",
            # 2. Sub Fund
            "2",
            "30",
            "Snacks",
            "2025-01-02",
            "",
            # 3. back
            "3",
        ]
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.fund_editor(self.system)

        df = self.system.get_df()
        self.assertGreaterEqual(len(df), 2)

    # ========= CLI: log_viewer =========

    def test_log_viewer_print_search_filter_summary_and_exit(self):
        # prepare some logs
        self.system.add_fund(200, "Income")
        self.system.sub_fund(50, "Food")

        inputs = [
            # 1. Print full log with blank date range
            "1",
            "",   # start
            "",   # end
            "",   # Enter to return
            # 2. Search
            "2",
            "Income",
            "",
            # 3. Filter status (choose succeeded)
            "3",
            "1",  # succeeded
            "",
            # 4. Summary
            "4",
            "2025-01",  # start
            "2025-01",  # end
            "",
            # 5. Back to main
            "5",
        ]
        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.log_viewer(self.system)

    # ========= CLI: property_editor =========

    def _prepare_member_and_asset(self):
        g = guardian("Parent", "G1", "1980-01-01", income=80000, job_title="Engineer")
        self.system.add_member(g)
        asset = self.system.add_asset_for_member("G1", "Car", "Vehicle", 20000)
        return asset

    def test_property_editor_add_asset_via_cli_and_exit(self):
        g = guardian("Parent", "G1", "1980-01-01", income=80000, job_title="Engineer")
        self.system.add_member(g)

        inputs = [
            # 1. Add new asset
            "1",          # menu choice
            "Car",        # name
            "20000",      # value
            "1",          # asset type index
            "1",          # owner index
            "2024-01-01", # date acquired
            "",           # Enter
            # Back to main
            "5",
        ]

        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.property_editor(self.system)

        self.assertEqual(len(self.system.property_registry), 1)

    def test_property_editor_edit_asset_flow(self):
        asset = self._prepare_member_and_asset()
        asset_id = asset.asset_id

        inputs = [
            # outer menu: edit existing asset
            "2",
            asset_id,
            # inner: edit name
            "1",
            "Renamed Asset",
            "",
            # inner: edit value
            "2",
            "9999",
            "",
            # inner: edit type
            "3",
            "1",   # choose first type
            "",
            # inner: edit owner
            "4",
            "1",   # choose first member
            "",
            # inner: back
            "5",
            # outer: quit
            "5",
        ]

        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.property_editor(self.system)

        # confirm asset got updated
        self.assertEqual(len(self.system.property_registry), 1)

    def test_property_editor_delete_and_reports_and_exit(self):
        asset = self._prepare_member_and_asset()
        asset_id = asset.asset_id

        inputs = [
            # 3. Delete asset
            "3",
            asset_id,
            "y",
            "",
            # 4. Reports & analysis
            "4",
            # inner: 1. List all assets
            "1",
            "",
            # inner: 2. Asset summary
            "2",
            "",
            # inner: 3. Search assets
            "3",
            "Car",
            "",
            # inner: 4. Visualization data (by Owner)
            "4",
            "2",
            "",
            # inner: back
            "5",
            # outer: back
            "5",
        ]

        with patch("budget_system.budget_system.clear_screen"), \
             patch("budget_system.budget_system.time.sleep"), \
             patch("budget_system.budget_system.input", side_effect=inputs):
            bs.property_editor(self.system)
