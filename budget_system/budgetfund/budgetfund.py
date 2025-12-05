import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class InsufficientFundsError(Exception):
    """Raised when a fund does not have enough balance for an operation."""
    pass


class budgetfund:  # this is the class for the whole budget of the family
    log_title = ['action', 'amount', 'description', 'balance', 'status', 'date']

    def __init__(self, opening_balance, name=''):
        self.opening_balance = float(opening_balance)
        self.__balance = float(opening_balance)
        self.household_name = name
        self.__log = []   # 每条记录: [action, amount, description, balance, status, date]

    # ---------- 1. 带异常处理的校验 ----------
    def get_log(self):
        """Return raw log structure: [title_list, list_of_records]."""
        return [self.log_title, self.__log]
    
    def validate(self, amount=0, raise_error: bool = False):
        """Check if there is enough balance.

        Parameters
        ----------
        amount : float
            The amount to validate.
        raise_error : bool
            If True, raise InsufficientFundsError when balance is not enough.
            If False, simply return False in that case.

        Returns
        -------
        bool
            True if validation passes, False otherwise (when raise_error=False).
        """
        try:
            amount = float(amount)

            if amount < 0:
                # 这个是明显的参数错误，直接抛没问题
                raise ValueError("Amount must be non-negative.")

            if amount > self.__balance:
                msg = f"Insufficient balance: need {amount}, current {self.__balance}"
                if raise_error:
                    # 给内部（例如 sub）使用：触发自定义异常
                    raise InsufficientFundsError(msg)
                else:
                    # 给外部 / tests 使用：返回 False
                    print(f"[ERROR] {msg}")
                    return False

            return True

        except TypeError as e:
            print(f"[ERROR] Invalid amount type: {e}")
            raise


    # ---------- 2. add：正常加钱 + 记一条 succeeded 记录 ----------
    def add(self, amount, desciption='', date=None):
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")
        amount = float(amount)
        self.__balance += amount
        self.__log.append(['add', amount, desciption, self.get(), 'succeeded', date])
        return True

    # ---------- 3. sub：带异常处理、成功/失败都写 log ----------
    def sub(self, amount, description="", date=None):
        """Subtract an expense from the fund, with error handling."""
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")
        try:
            self.validate(amount, raise_error=True)

            amount = float(amount)
            self.__balance -= amount
            self.__log.append(['sub', amount, description, self.get(), 'succeeded', date])
            return True

        except InsufficientFundsError:
            self.__log.append(['sub', float(amount), description, self.get(), 'failed', date])
            print("[ERROR] Transaction failed due to insufficient funds.")
            return False

        except Exception as e:
            print(f"[ERROR] Unexpected error in sub(): {e}")
            raise


    # ---------- 4. 一些 getter ----------
    def get(self):
        return self.__balance

    def get_df(self, start=None, end=None):
        """
        Return log as DataFrame within [start, end], always with 'year_month' column.

        start, end:
            - None: 不限制
            - "YYYY-MM" 或 "YYYY-MM-DD" 都可以。我们会按“整月”范围来筛选。
        """
        try:
            # 用完整列名构建 DataFrame
            df = pd.DataFrame(self.__log, columns=self.log_title)

            # 空表：也要带上 year_month 列
            if df.empty:
                df["year_month"] = pd.Series(dtype="object")
                return df

            # 转 datetime
            df["date"] = pd.to_datetime(df["date"])

            # 先算 year_month，后面测试要用
            df["year_month"] = df["date"].dt.to_period("M").astype(str)  # e.g. "2025-01"

            # 如果提供了 start / end，就按“月区间”筛选
            if start is not None:
                # 不管传 "2025-01" 还是 "2025-01-15"，都转成对应的月份
                p_start = pd.Period(start, freq="M")
                start_ts = p_start.to_timestamp(how="start")
                df = df[df["date"] >= start_ts]

            if end is not None:
                p_end = pd.Period(end, freq="M")
                end_ts = p_end.to_timestamp(how="end")
                df = df[df["date"] <= end_ts]

            return df

        except KeyError as e:
            print(f"[ERROR] Missing expected column in log: {e}")
            raise
        except (TypeError, ValueError) as e:
            print(f"[ERROR] Invalid date format for start/end: {e}")
            raise


    # ---------- 6. summarize_month 保持逻辑，用修好的 get_df ----------
    def summarize_month(self, start_month, end_month=''):
        if end_month == '':
            end_month = start_month
        df = self.get_df().copy()
        if df.empty:
            print("No transaction records.")
            return None

        df["date"] = pd.to_datetime(df["date"])

        start = pd.to_datetime(start_month)
        end = pd.to_datetime(end_month) + pd.offsets.MonthEnd(0)

        period_df = df[(df["date"] >= start) & (df["date"] <= end)]
        if period_df.empty:
            print("No transactions in this period.")
            return None

        success_df = period_df[period_df["status"] == "succeeded"].sort_values("date")
        if success_df.empty:
            print("No succeeded transaction in this period.")
            return None

        income = success_df[success_df["action"] == "add"]["amount"].sum()
        expense = success_df[success_df["action"] == "sub"]["amount"].sum()

        first = success_df.iloc[0]
        if first["action"] == "add":
            opening_balance = first["balance"] - first["amount"]
        else:
            opening_balance = first["balance"] + first["amount"]

        closing_balance = success_df.iloc[-1]["balance"]

        labels = ["Opening", "Income", "Expense", "Closing"]
        values = [opening_balance, income, expense, closing_balance]

        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.bar(labels, values)
        plt.title(f"Summary for {start_month} → {end_month}")
        plt.ylabel("Amount")
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        df_exp = success_df[success_df["action"] == "sub"]

        plt.subplot(1, 2, 2)
        if df_exp.empty:
            plt.text(0.5, 0.5, "No expenses", ha="center", va="center", fontsize=12)
            plt.title(f"Expense Breakdown {start_month} → {end_month}")
        else:
            category_sum = df_exp.groupby("description")["amount"].sum()
            plt.pie(category_sum, labels=category_sum.index, autopct="%1.1f%%")
            plt.title(f"Expense Breakdown {start_month} → {end_month}")

        plt.tight_layout()
        plt.show()

    def __str__(self):
        return 'The family budget of ' + self.household_name + ' is: ' + str(self.get())
