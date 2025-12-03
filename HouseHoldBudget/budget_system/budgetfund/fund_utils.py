from .budgetfund import budgetfund
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display

def print_log(budgetfund,start,end):
    df = budgetfund.get_df(start,end)
    def color_status(val):  # pragma: no cover
        if val == 'succeeded':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'failed':
            return 'background-color: #f8d7da; color: #721c24;'
        return ""
    styler = df.style
    styler = styler.map(color_status, subset="status")

    display(styler)

    return [df.values.tolist(), f"Total Record #: {len(df)}"]


def search_log(budgetfund, keyword=''):
    df = budgetfund.get_df().copy()
    df['description'] = df['description'].fillna("")
    found = df[df['description'].str.contains(keyword, case=False, na=False)]
    if found.empty:
        return ["No record found"]
    def color_status(val):  # pragma: no cover
        if val == 'succeeded':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'failed':
            return 'background-color: #f8d7da; color: #721c24;'
        return ""
    styler = found.style.map(color_status, subset="status")
    display(styler)
    return [found.values.tolist(), f"Total # of Record Found is: {len(found)}"]
    

def filter_status(budgetfund, status=True):
    df = budgetfund.get_df().copy()
    target = 'succeeded' if status else 'failed'
    found = df[df['status'] == target]
    if found.empty:
        return "No record found"
    def color_status(val):  # pragma: no cover
        if val == 'succeeded':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'failed':
            return 'background-color: #f8d7da; color: #721c24;'
        return ""
    styler = found.style.map(color_status, subset="status")
    display(styler)
    return [found.values.tolist(), f"Total # of Record Found is: {len(found)}"]