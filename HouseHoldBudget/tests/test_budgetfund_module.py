import unittest
from unittest.mock import patch

from budget_system.budgetfund.budgetfund import budgetfund
from budget_system.budgetfund.fund_utils import (
    print_log,
    search_log,
    filter_status,
)


class TestBudgetFundModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n[setUpClass] TestBudgetFundModule")

    @classmethod
    def tearDownClass(cls):
        print("[tearDownClass] TestBudgetFundModule\n")

    def setUp(self):
        self.fund = budgetfund(opening_balance=1000, name="Test Household")

    def tearDown(self):
        print("[tearDown] Finished one TestBudgetFundModule test method")

    # ========= basic add / sub / log =========

    def test_add_and_sub(self):
        # opening balance
        self.assertEqual(self.fund.get(), 1000.0)

        # add
        result_add = self.fund.add(200, "Salary")
        self.assertTrue(result_add)
        self.assertEqual(self.fund.get(), 1200.0)

        # sub success
        result_sub = self.fund.sub(300, "Grocery")
        self.assertTrue(result_sub)
        self.assertEqual(self.fund.get(), 900.0)

        # get_log structure
        log = self.fund.get_log()
        # [0] = title list, [1] = list of records
        self.assertEqual(len(log), 2)
        self.assertIsInstance(log[0], list)
        self.assertIsInstance(log[1], list)

    def test_validate_and_failed_transaction(self):
        # validate True
        self.assertTrue(self.fund.validate(500))
        # validate False
        self.assertFalse(self.fund.validate(5000))

        # failed sub should not change balance
        result = self.fund.sub(5000, "Big Purchase")
        self.assertFalse(result)
        self.assertEqual(self.fund.get(), 1000.0)

        # log should have one failed record
        df = self.fund.get_df()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["status"], "failed")

    # ========= get_df & year_month =========

    def test_get_df_empty_then_with_range(self):
        # no log yet
        df_empty = self.fund.get_df()
        self.assertTrue(df_empty.empty)
        self.assertIn("year_month", df_empty.columns)

        # add records in different months
        self.fund.add(100, "Salary Jan", date="2025-01-10")
        self.fund.sub(20, "Food Jan", date="2025-01-15")
        self.fund.add(300, "Salary Feb", date="2025-02-05")

        df_all = self.fund.get_df()
        self.assertEqual(len(df_all), 3)

        # filter only January
        df_jan = self.fund.get_df(start="2025-01", end="2025-01")
        self.assertEqual(len(df_jan), 2)
        self.assertTrue((df_jan["year_month"] == "2025-01").all())

        # start=None, end specific
        df_until_jan = self.fund.get_df(start=None, end="2025-01")
        self.assertEqual(len(df_until_jan), 2)

        # start specific, end=None
        df_from_feb = self.fund.get_df(start="2025-02", end=None)
        self.assertEqual(len(df_from_feb), 1)
        self.assertTrue((df_from_feb["year_month"] == "2025-02").all())

    # ========= summarize_month =========

    def test_summarize_month_no_transactions(self):
        # no records at all
        with patch("budget_system.budgetfund.budgetfund.plt.show"):
            result = self.fund.summarize_month("2025-01")
        self.assertIsNone(result)

    def test_summarize_month_no_transactions_in_period(self):
        # records exist but not in target period
        self.fund.add(100, "Salary Jan", date="2025-01-10")
        self.fund.sub(30, "Food Jan", date="2025-01-15")

        with patch("budget_system.budgetfund.budgetfund.plt.show"):
            result = self.fund.summarize_month("2024-01", "2024-01")
        self.assertIsNone(result)

    def test_summarize_month_only_failed_transactions(self):
        # only failed transactions in the period
        self.fund.sub(5000, "Big Purchase", date="2025-01-10")  # failed

        with patch("budget_system.budgetfund.budgetfund.plt.show"):
            result = self.fund.summarize_month("2025-01", "2025-01")
        self.assertIsNone(result)

    def test_summarize_month_normal_case(self):
        # successful add/sub should go through full plotting path
        self.fund.add(500, "Salary", date="2025-01-05")
        self.fund.sub(100, "Food", date="2025-01-10")
        self.fund.sub(50, "Snacks", date="2025-01-15")

        with patch("budget_system.budgetfund.budgetfund.plt.show") as mock_show:
            result = self.fund.summarize_month("2025-01", "2025-01")

        # function returns None but should have called plt.show once
        self.assertIsNone(result)
        mock_show.assert_called_once()

    # ========= __str__ =========

    def test_str_representation(self):
        text = str(self.fund)
        self.assertIn("Test Household", text)
        self.assertIn("family budget", text.lower())

    # ========= fund_utils: print_log =========

    def test_print_log_basic(self):
        # prepare some records
        self.fund.add(100, "Salary", date="2025-01-05")
        self.fund.sub(20, "Food", date="2025-01-06")

        with patch("budget_system.budgetfund.fund_utils.display"):
            result = print_log(self.fund, start="2025-01", end="2025-12")

        # result should be [records_list, summary_string]
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        records, summary = result
        self.assertGreaterEqual(len(records), 2)
        self.assertIn("Total Record #:", summary)

    # ========= fund_utils: search_log =========

    def test_search_log_found_and_not_found(self):
        self.fund.add(100, "Salary", date="2025-01-05")
        self.fund.add(50, "Gift", date="2025-01-06")
        self.fund.sub(10, "Snacks", date="2025-01-07")

        with patch("budget_system.budgetfund.fund_utils.display"):
            # search for "sal" -> should match "Salary" only
            result_found = search_log(self.fund, "sal")
            self.assertIsInstance(result_found, list)
            self.assertEqual(len(result_found), 2)
            records, summary = result_found
            self.assertEqual(len(records), 1)
            self.assertIn("Total # of Record Found is:", summary)

            # search for something not in descriptions
            result_not_found = search_log(self.fund, "xyz")
            self.assertEqual(result_not_found, ["No record found"])

    # ========= fund_utils: filter_status =========

    def test_filter_status_succeeded_and_failed(self):
        # one succeeded add, one succeeded sub, one failed sub
        self.fund.add(100, "Salary", date="2025-01-05")
        self.fund.sub(10, "Food", date="2025-01-06")
        self.fund.sub(99999, "Too Big", date="2025-01-07")  # failed

        with patch("budget_system.budgetfund.fund_utils.display"):
            # succeeded records
            res_succeeded = filter_status(self.fund, status=True)
            self.assertIsInstance(res_succeeded, list)
            records_succ, summary_succ = res_succeeded
            self.assertGreaterEqual(len(records_succ), 2)
            self.assertIn("Total # of Record Found is:", summary_succ)

            # failed records
            res_failed = filter_status(self.fund, status=False)
            if isinstance(res_failed, str):
                # no record case
                self.assertEqual(res_failed, "No record found")
            else:
                records_fail, summary_fail = res_failed
                self.assertGreaterEqual(len(records_fail), 1)
                self.assertIn("Total # of Record Found is:", summary_fail)
	
    def test_filter_status_no_records(self):
    # 新建一个完全没有交易记录的 fund
        empty_fund = budgetfund(opening_balance=0, name="Empty Fund")

        # 即使我们 patch 了 display，这个分支也不会调用 display，
        # 但 patch 一样是安全的
        with patch("budget_system.budgetfund.fund_utils.display"):
            result = filter_status(empty_fund, status=True)

        # 这里的返回值在源码里就是这个字符串
        self.assertEqual(result, "No record found")
