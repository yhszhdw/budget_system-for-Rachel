import unittest
from unittest.mock import patch

from budget_system.member.member_type import dependant, guardian, member_edit


class TestMemberTypeModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n[setUpClass] MemberType tests start")

    @classmethod
    def tearDownClass(cls):
        print("[tearDownClass] MemberType tests end\n")

    def setUp(self):
        self.dep = dependant("Child", "D001", "2015-01-01")
        self.guard = guardian(
            "Parent", "G001", "1980-01-01",
            income=50000, job_title="Teacher"
        )

    def tearDown(self):
        print("[tearDown] Completed one MemberType test")

    # ========= basic dependant / guardian behavior =========

    def test_dependant_basic(self):
        # Test dependant attributes and updates
        self.assertEqual(self.dep.name, "Child")
        self.assertEqual(self.dep.ID, "D001")
        self.assertEqual(self.dep.type, "dependant")

        # member base methods (from member class)
        self.dep.new_name("New Child")
        self.dep.new_ID("D001-X")
        self.dep.new_DOB("2016-02-02")

        self.assertEqual(self.dep.name, "New Child")
        self.assertEqual(self.dep.ID, "D001-X")
        self.assertEqual(self.dep.DOB, "2016-02-02")

        s = str(self.dep)
        self.assertIn("New Child", s)
        self.assertIn("Dependant", s)

    def test_guardian_job_and_income(self):
        # Test guardian job and income behavior
        self.assertEqual(self.guard.job_title, "Teacher")
        self.assertEqual(self.guard.income, 50000)
        self.assertEqual(self.guard.type, "guardian")

        self.guard.new_job("Engineer")
        self.guard.new_income(80000)

        self.assertEqual(self.guard.job_title, "Engineer")
        self.assertEqual(self.guard.get_income(), 80000)

        s = str(self.guard)
        self.assertIn("Engineer", s)
        self.assertIn("Guardian", s)
        self.assertIn("Income", s)

    # ========= member_edit for dependant =========

    def test_member_edit_dependant_edit_name_and_dob(self):
        """
        依次选择:
        1 -> 编辑名字
        2 -> 编辑 DOB
        3 -> 退出
        """
        inputs = [
            "1",            # edit name
            "Dep New",      # new_name
            "2",            # edit DOB
            "2010-12-31",   # new_DOB
            "3",            # exit
        ]
        with patch("budget_system.member.member_type.input", side_effect=inputs):
            member_edit(self.dep)

        self.assertEqual(self.dep.name, "Dep New")
        self.assertEqual(self.dep.DOB, "2010-12-31")

    def test_member_edit_dependant_invalid_choice(self):
        """
        先输入一个无效选项，然后再输入 3 退出，
        覆盖 'Invalid choice' 分支。
        """
        inputs = [
            "9",  # invalid
            "3",  # exit
        ]
        with patch("budget_system.member.member_type.input", side_effect=inputs):
            member_edit(self.dep)

        # 不应该修改原始信息
        self.assertEqual(self.dep.name, "Child")
        self.assertEqual(self.dep.DOB, "2015-01-01")

    # ========= member_edit for guardian =========

    def test_member_edit_guardian_edit_all_fields(self):
        """
        guardian 菜单:
        1 -> name
        2 -> DOB
        3 -> job + income
        4 -> income
        5 -> exit
        """
        inputs = [
            # 1. Edit name
            "1",
            "Guard New",
            # 2. Edit DOB
            "2",
            "1979-12-31",
            # 3. Edit job + income
            "3",
            "Senior Dev",   # new_job
            "90000",        # new_income for job
            # 4. Edit income only
            "4",
            "95000",        # new_income
            # 5. Exit editor
            "5",
        ]
        with patch("budget_system.member.member_type.input", side_effect=inputs):
            member_edit(self.guard)

        self.assertEqual(self.guard.name, "Guard New")
        self.assertEqual(self.guard.DOB, "1979-12-31")
        self.assertEqual(self.guard.job_title, "Senior Dev")
        self.assertEqual(self.guard.income, 95000)

    def test_member_edit_guardian_invalid_choice(self):
        """
        guardian 菜单下先输入无效选项，再退出，
        覆盖 'Invalid choice. Please try again.' 分支。
        """
        inputs = [
            "9",  # invalid
            "5",  # exit
        ]
        with patch("budget_system.member.member_type.input", side_effect=inputs):
            member_edit(self.guard)

        # 原始信息不变
        self.assertEqual(self.guard.name, "Parent")
        self.assertEqual(self.guard.job_title, "Teacher")
        self.assertEqual(self.guard.income, 50000)

    # ========= member_edit: unknown type branch =========

    def test_member_edit_unknown_type(self):
        """
        构造一个 type 不是 'dependant' / 'guardian' 的对象，
        直接走 Unknown member type 分支。
        """
        class FakeMember:
            def __init__(self):
                self.type = "alien"
                self.name = "X"
                self.ID = "M999"
                self.DOB = "1900-01-01"

        fake = FakeMember()
        # 该分支不会调用 input，所以无需 patch
        member_edit(fake)
        # 只要不中断、不报错就算覆盖到了这个分支
