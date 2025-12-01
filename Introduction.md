# 🧾 1. Subpackage: `member`

This subpackage defines household members using inheritance.  
It consists of **two modules**, each containing classes and methods.

---

# 📄 Module 1: `member.py` — Base Member Class

### Class: `member`

| Method | Description |
|--------|-------------|
| `__init__(name, ID, DOB)` | Create a basic member with name, unique ID, and date of birth. |
| `new_name(name)` | Modify member name. |
| `new_DOB(DOB)` | Modify member date of birth. |
| `new_ID(ID)` | Modify member ID. |
| `get_age()` | Compute age in years from DOB. |

This is the **parent class** for all member types.

---

# 📄 Module 2: `member_type.py` — Member Types & Editor

### Class: `dependant(member)`
| Method | Description |
|--------|-------------|
| `__init__(...)` | Create a dependant (child or non-working member). |
| `__str__()` | Human-readable dependant information. |
| *(inherits all methods from `member`)* | — |

---

### Class: `guardian(member)`
| Method | Description |
|--------|-------------|
| `__init__(..., income, job_title='')` | Create a guardian with job and income. |
| `new_job(job_title)` | Update job title. |
| `new_income(income)` | Update income amount. |
| `get_income()` | Return income. |
| `__str__()` | Human-readable guardian profile. |

---

### Function: `member_edit(member_obj)`
Interactive CLI editor that allows:
- (For dependants) edit name or DOB  
- (For guardians) edit name, DOB, job, income  
Uses polymorphism based on member type.

---

# 💰 2. Subpackage: `budgetfund`

Handles all financial activity: income, expenses, logs, summaries, and visualizations.  
Contains **two modules**.

---

# 📄 Module 1: `budgetfund.py` — Fund Class

### Class: `budgetfund`

| Method | Description |
|--------|-------------|
| `__init__(opening_balance, name='')` | Initialize fund account with balance. |
| `validate(amount=0)` | Check if balance is sufficient. |
| `add(amount, description='', date=None)` | Add income and log success. |
| `sub(amount, description='', date=None)` | Subtract expense; success/fail logged. |
| `get()` | Return current balance. |
| `get_log()` | Return internal log list. |
| `get_df(start=None, end=None)` | Log as DataFrame with filtering. |
| `summarize_month(start, end='')` | Monthly financial summary (bar + pie chart). |
| `__str__()` | Summary description of fund account. |

---

# 📄 Module 2: `fund_utils.py` — Log Formatting & Searching

### Function: `print_log(budgetfund, start, end)`
Return and display logs in a color-formatted table.

### Function: `search_log(budgetfund, keyword)`
Case-insensitive search in description field.

### Function: `filter_status(budgetfund, status=True)`
Return only succeeded or failed transaction records.

---

# 🏡 3. Subpackage: `property`

Manages all household assets such as houses, cars, and investments.  
Includes **two modules**.

---

# 📄 Module 1: `asset.py` — Asset & Registry Classes

### Class: `Asset`

| Method | Description |
|--------|-------------|
| `__init__(name, asset_type, owner, current_value, date_acquired)` | Create an asset with auto ID and validation. |
| `_generate_id(asset_type)` | Internal ID generator (A001R, etc.). |
| `update_value(new_value)` | Update asset value (auto timestamp). |
| `to_dict()` | Convert to record for DataFrame. |
| `__str__()` | Human-readable asset summary. |

---

### Class: `PropertyRegistry`

| Method | Description |
|--------|-------------|
| `add_asset(asset)` | Add an asset to registry. |
| `delete_asset(asset_id)` | Remove asset by ID. |
| `update_asset_value(asset_id, new_value)` | Update an existing asset’s value. |
| `get_asset(asset_id)` | Return asset object. |
| `to_dataframe()` | Convert all assets to a DataFrame. |
| `filter_assets(asset_type=None, owner=None)` | Filter assets by type or owner. |
| `__iter__()` | Allow looping through assets. |

---

# 📄 Module 2: `asset_utils.py` — Summary, Search, Visualization

### Function: `summarize_total_value(registry)`
Aggregate total, average, and count grouped by Type/Owner.

### Function: `search_assets(registry, keyword)`
Search based on ID, name, type, or owner.

### Function: `get_visualization_data(registry, group_by='Type')`
Generate a summary table + pie chart visualization.

---

# 🏠 4. Main Controller: `BudgetSystem`

The `BudgetSystem` class integrates all three sub-packages (member, budgetfund, property).  
It serves as the central interface that manages **members**, **funds**, and **assets** together.

---

## 👥 Member Management

| Method | Description |
|--------|-------------|
| `add_member(member)` | Add a new member (guardian or dependant). |
| `remove_member(ID)` | Remove a member by unique ID. |
| `list_member()` | Print all members in the system. |
| `get_member(ID)` | Retrieve a member object by ID. |
| `upgrade_member(ID)` | Convert a dependant into a guardian (promote role). |
| `__str__()` | Return formatted summary of the BudgetSystem state. |

---

## 💰 Fund Management

| Method | Description |
|--------|-------------|
| `add_fund(amount, description, date)` | Add income to the budget fund. |
| `sub_fund(amount, description, date)` | Subtract expenses; logs success/failed. |
| `validate_fund(amount)` | Check whether fund has enough balance. |
| `summarize_month(start, end)` | Generate monthly summary bar/pie charts. |
| `filter_fund_status(status)` | Filter logs by succeeded/failed status. |
| `search_fund_log(keyword)` | Search transaction logs by description keyword. |
| `get_df(start, end)` | Return fund logs as a DataFrame. |
| `print_fund_log(start, end)` | Pretty-print log using styled DataFrame. |

---

## 🏡 Property / Asset Management

| Method | Description |
|--------|-------------|
| `add_asset_for_member(id, name, type, value, date)` | Add an asset linked to a specific member. |
| `list_assets()` | Display all assets in table format. |
| `delete_asset(asset_id)` | Remove asset by ID. |
| `update_asset_value(asset_id, new_value)` | Change asset value with timestamp update. |
| `summarize_assets()` | Table summary grouped by type/owner. |
| `search_assets(keyword)` | Search assets by ID/name/type/owner. |
| `get_asset_visualization_data(group_by)` | Generate table + pie chart visualization. |

---

## 🖥️ CLI Interactive Menu System

| Method | Description |
|--------|-------------|
| `main_menu(system)` | Root menu for all operations. |
| `member_editor(system)` | Menu interface for adding/editing/deleting members. |
| `fund_editor(system)` | Menu for income/expense operations. |
| `property_editor(system)` | Menu for asset creation & modification. |
| `log_viewer(system)` | Menu for viewing/searching/filtering fund logs. |
| `initialization(system=None)` | Initialize a new system or re-enter menu. |

---

# ✔ Summary

This package provides:

- Complete household management  
- Modular structure with 3 sub-packages  
- Inheritance-based member hierarchy  
- Full financial logging system  
- Asset management with summaries & visualizations  
- Optional menus for interactive use  

It fulfills the typical requirements for a multi-module Python package with sub-packages, OOP design, and documentation.

---
