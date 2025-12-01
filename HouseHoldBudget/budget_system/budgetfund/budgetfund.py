import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class budgetfund: #this is the class for the whole budget of the family
    log_title=['action','amount','description','balance','status','date']
    
    def __init__(self,opening_balance,name=''):
        
        self.opening_balance=float(opening_balance)
        self.__balance=float(opening_balance)
        self.household_name=name
        self.__log=[]
        
    def validate(self,amount=0): #see if the balance is larger or equal to a certain amount,if no value entered, check if the account is in debt
        if self.__balance>=float(amount):
            return True
        return False
        
    def add(self,amount,desciption='',date=None):
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")
        self.__balance+=float(amount)
        self.__log.append(['add',amount,desciption,self.get(),'succeeded',date])
        return True
        
    def sub(self,amount,desciption='',date=None):
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")    
        if self.validate(amount):
            self.__balance-=float(amount)
            self.__log.append(['sub',amount,desciption,self.get(),'succeeded',date])
            return True
        self.__log.append(['sub',amount,desciption,self.get(),'failed',date])
        return False
            
    def get(self):
        return self.__balance
        
    def get_log(self):
        return [self.log_title,self.__log]
        
    def get_df(self,start=None, end=None):
        if not self.__log:
            return pd.DataFrame(columns=self.log_title + ["year_month"])
    
        df = pd.DataFrame([
            {key: entry[i] for i, key in enumerate(self.log_title)}
            for entry in self.__log
        ])

        df["date"] = pd.to_datetime(df["date"])
        df["year_month"] = df["date"].dt.strftime("%Y-%m")
        if start is None and end is None:
            return df
        if start is None:
            start = df["year_month"].min()
        if end is None:
            end = df["year_month"].max()
        return df[(df["year_month"] >= start) & (df["year_month"] <= end)]

    def summarize_month(self, start_month, end_month=''):
        if end_month=='':
            end_month=start_month
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
        return('The family budget of '+ self.household_name +' is: '+ str(self.get()))

