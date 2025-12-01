from .budgetfund import budgetfund, fund_utils
from .member.member_type import guardian, dependant, member_edit
from .property.asset import Asset, PropertyRegistry
from .property.asset_utils import summarize_total_value, search_assets, get_visualization_data
from IPython.display import clear_output
import time
from datetime import datetime

class BudgetSystem:
    def __init__(self, current_fund, address, household_name='', members=None):
        # please enter member as a list of dependant and guardian
        self.fund = budgetfund(current_fund, household_name)
        self.address = address
        self.household_name = household_name
        if members==None:
            self.members=[]
        else:
            self.members = members
        self.property_registry = PropertyRegistry()

    # -------- member methods --------
    def add_member(self, new_member):
        if any(m.ID == new_member.ID for m in self.members):
            print(f"Warning: member with ID {new_member.ID} already exists.")
            return False
        self.members.append(new_member)
        return True

    def remove_member(self, ID):
        for person in self.members:
            if person.ID == ID:
                self.members.remove(person)
                return True
        return False

    def list_member(self):
        if not self.members:
            print("No members in the system.")
            return
        for person in self.members:
            print(person)

    def get_member(self, ID):
        for person in self.members:
            if person.ID == ID:
                return person
        return None

    def upgrade_member(self, ID):
        person = self.get_member(ID)
        if person is None:
            print('No member found')
            return False
        elif person.type == 'guardian':
            print('Member already a guardian')
            return False
        else:
            job = input('Please enter the job title for the member: ')
            income = float(input('Please enter the income for the member: '))
            self.remove_member(ID)
            new_person = guardian(person.name, person.ID, person.DOB, income, job)
            self.add_member(new_person)
            return True

    def __str__(self):
        return (f"Budget System for {self.household_name}\n"
                f"Address: {self.address}\n"
                f"Members: {len(self.members)}\n"
                f"Current Fund: {self.fund.get()}")

    # -------- fund methods --------
    def print_fund_log(self, start, end):
        return fund_utils.print_log(self.fund, start, end)

    def search_fund_log(self, keyword=''):
        return fund_utils.search_log(self.fund, keyword)

    def filter_fund_status(self, status=True):
        return fund_utils.filter_status(self.fund, status)

    def add_fund(self, amount, description='', date=None):
        return self.fund.add(amount, description, date)

    def sub_fund(self, amount, description='', date=None):
        return self.fund.sub(amount, description, date)

    def visualize(self, year_month):
        return self.fund.summarize_month(year_month)

    def validate_fund(self, amount=0):
        return self.fund.validate(amount)

    def summarize_month(self, start_month, end_month=''):
        if end_month == '':
            return self.fund.summarize_month(start_month, start_month)
        return self.fund.summarize_month(start_month, end_month)

    def get_df(self, start=None, end=None):
        return self.fund.get_df(start, end)

    # -------- property / asset methods --------
    def add_asset_for_member(self, member_id, name, asset_type, current_value, date_acquired=None):
        """Create an asset for a given member ID and add it to the registry."""
        member = self.get_member(member_id)
        if member is None:
            print(f"No member found with ID {member_id}. Cannot add asset.")
            return None

        try:
            asset = Asset(
                name=name,
                asset_type=asset_type,
                current_value=current_value,
                owner=member_id,          # store owner as member ID
                date_acquired=date_acquired
            )
        except ValueError as e:
            print(f"Failed to create asset: {e}")
            return None

        self.property_registry.add_asset(asset)
        return asset

    def list_assets(self):
        """Print all assets in the registry."""
        if len(self.property_registry) == 0:
            print("No assets in the system.")
            return
        for asset in self.property_registry:
            print(asset)

    def delete_asset(self, asset_id):
        """Delete an asset by ID."""
        return self.property_registry.delete_asset(asset_id)

    def update_asset_value(self, asset_id, new_value):
        """Update only the value of an asset."""
        return self.property_registry.update_asset_value(asset_id, new_value)

    def summarize_assets(self):
        """Return summary info: total value and summary table."""
        return summarize_total_value(self.property_registry)

    def search_assets(self, keyword):
        """Search assets by keyword."""
        return search_assets(self.property_registry, keyword)

    def get_asset_visualization_data(self, group_by="Type"):
        """Return aggregated data for charts."""
        return get_visualization_data(self.property_registry, group_by=group_by)



def initialization(system=None):
    if system==None:
        print('Welcome to the Family Budget System')
        print('Please follow the instruction to Initialize the system')
        house_hold_name=input('Please input your household name:')
        balance=float(input('Please input your available balance:'))
        ini_address=input('Please input your address:')
        system = BudgetSystem(
            members=[],
            current_fund=balance,
            address=ini_address,
            household_name=house_hold_name
        )
        input('First time setup complete, please initialize again with the given system:')
    else:
        main_menu(system)
    return system

def clear_screen():
    clear_output(wait=False)

def main_menu(system):
    while True:
        clear_screen()
        time.sleep(0.05)
        print("===== Family Budget System =====")
        print(system)
        print("--------------------------------")
        print("1. Member editor")
        print("2. Fund / Expense editor")
        print("3. Transaction log")
        print("4. Property Manager")
        print("5. Quit")
        print("--------------------------------")
        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            member_editor(system)
        elif choice == "2":
            fund_editor(system)
        elif choice == "3":
            log_viewer(system)
        elif choice == "4":
            property_editor(system)
        elif choice == "5":
            clear_screen()
            print("Thank you for using the system. Goodbye!")
            break
        else:
            print("Invalid choice.")
            input("Press Enter to try again...")

def member_editor(system):
    while True:
        clear_screen()
        time.sleep(0.05)
        print("=== Member Editor ===")
        print(system)
        print("------------------------------")

        print("Current members:")
        if len(system.members) == 0:
            print("  (No members yet)")
        else:
            for m in system.members:
                print("  " + str(m))

        print("\nOptions:")
        print("1. List members")
        print("2. Add member")
        print("3. Delete member")
        print("4. Upgrade member (dependant → guardian)")
        print("5. Edit member by ID")
        print("6. Back to main menu")
        print("------------------------------")
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            print("=== Member List ===")
            time.sleep(0.05)
            system.list_member()
            input("\nPress Enter to return...")

        elif choice == "2":
            print("=== Add Member ===")
            time.sleep(0.05)
            name = input("Name: ")
            dob = input("Date of birth (YYYY-MM-DD): ")
            ID = input("Unique ID: ")
            mtype = input("Type (guardian/dependant): ").strip().lower()

            if mtype == "guardian":
                job = input('Job Title: ')
                income = float(input('Income: '))
                new_member = guardian(name, ID, dob, income, job)
            else:
                new_member = dependant(name, ID, dob)

            system.add_member(new_member)
            print("\nMember successfully added.")
            input("Press Enter to return...")

        elif choice == "3":
            print("=== Delete Member ===")
            time.sleep(0.05)
            ID = input("Enter ID to delete: ").strip()

            if system.remove_member(ID):
                print(f"Member with ID {ID} removed.")
            else:
                print(f"No member found with ID {ID}.")
            input("\nPress Enter to return...")

        elif choice == "4":
            print("=== Upgrade Member (dependant → guardian) ===")
            time.sleep(0.05)
            ID = input("Enter ID to upgrade: ").strip()
            if system.upgrade_member(ID):
                print(f"Member with ID {ID} has been upgraded to guardian.")
            else:
                print("Upgrade failed")
            input("\nPress Enter to return...")

        elif choice == "5":
            print("=== Edit Member by ID ===")
            time.sleep(0.05)
            ID = input("Enter ID: ").strip()

            person = system.get_member(ID)
            if person:
                member_edit(person)
            else:
                print("\nNo member found with that ID.")

            input("\nPress Enter to return...")

        elif choice == "6":
            break

        else:
            print("Invalid choice.")
            input("Press Enter to try again...")

def fund_editor(system):
     while True:
        clear_screen()
        time.sleep(0.05)
        print("=== Fund Editor ===")
        print(system)
        print("------------------------------")
        print("\nOptions:")
        print("1. Add Fund")
        print("2. Sub Fund")
        print("3. Back to main menu")
        print("------------------------------")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            print("=== Add Fund ===")
            time.sleep(0.05)
            amount=float(input('Please enter amount:'))
            text=input('Please enter description:')
            date=input("Please enter date (YYYY-MM-DD): ")
            system.add_fund(amount,text,date)
            input("\nPress Enter to return...")

        elif choice == "2":
            print("=== Sub Fund ===")
            time.sleep(0.05)
            amount=float(input('Please enter amount:'))
            text=input('Please enter description:')
            date=input("Please enter date (YYYY-MM-DD): ")
            system.sub_fund(amount,text,date)
            input("\nPress Enter to return...")

        elif choice == "3":
            break

        else:
            print("Invalid choice.")
            input("Press Enter to try again...")

def log_viewer(system):
    while True:
        clear_screen()
        time.sleep(0.05)
        print("=== Fund Log Viewer ===")
        print(f"Household: {system.household_name}")
        print("------------------------------")
        print("1. Print full fund log")
        print("2. Search fund log by keyword")
        print("3. Filter fund log by status")
        print("4. Monthly / period summary")
        print("5. Back to main menu")
        print("------------------------------")
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            print("=== Print Fund Log ===")
            time.sleep(0.05)
            print("You can enter a date range to filter the log.")
            print("Leave blank to use full range.")
            start = input("Start date (YYYY-MM-DD, or blank for no limit): ").strip()
            end   = input("End date   (YYYY-MM-DD, or blank for no limit): ").strip()

            start = start or None
            end   = end or None

            system.print_fund_log(start, end)
            input("\nPress Enter to return...")

        elif choice == "2":
            print("=== Search Fund Log ===")
            time.sleep(0.05)
            keyword = input("Enter keyword to search in description: ")
            system.search_fund_log(keyword)
            input("\nPress Enter to return...")

        elif choice == "3":
            print("=== Filter Fund Log by Status ===")
            time.sleep(0.05)
            print("Do you want to see:")
            print("1. Succeeded records")
            print("2. Failed records")
            status_choice = input("Choose (1/2): ").strip()
            if status_choice == "1":
                flag = True   # succeeded
            elif status_choice == "2":
                flag = False  # failed
            else:
                print("Invalid choice.")
                input("Press Enter to return...")
                continue
            system.filter_fund_status(flag)
            input("\nPress Enter to return...")

        elif choice == "4":
            print("=== Fund Summary ===")
            time.sleep(0.05)
            print("Please enter the summary period.")
            print("For monthly summary, you can use year-month format like 2025-05.")
            start = input("Start (e.g., 2025-05): ").strip()
            end   = input("End   (e.g., 2025-05): ").strip()
            system.summarize_month(start, end)
            input("\nPress Enter to return...")

        elif choice == "5":
            break

        else:
            print("Invalid choice.")
            input("Press Enter to try again...")

def property_editor(system):
    """
    CLI editor for assets using BudgetSystem methods.
    """
    registry = system.property_registry

    def choose_owner_id() -> str:
        """Pick owner (member ID) by number."""
        if not system.members:
            print("No members in the system. Please add members first.")
            input("Press Enter to return...")
            return ""

        print("Current members:")
        system.list_member()  # reuse existing method
        print("\nSelect owner:")
        for i, m in enumerate(system.members, start=1):
            print(f"{i}. {m.name} (ID: {m.ID})")

        while True:
            choice = input("Choose owner by number: ").strip()
            if not choice.isdigit():
                print("Please enter a number.")
                continue
            idx = int(choice)
            if 1 <= idx <= len(system.members):
                return system.members[idx - 1].ID
            else:
                print("Invalid choice. Try again.")

def property_editor(system):
    """
    CLI editor for assets using BudgetSystem methods.
    """
    registry = system.property_registry

    def choose_owner_id() -> str:
        """Pick owner (member ID) by number."""
        if not system.members:
            print("No members in the system. Please add members first.")
            input("Press Enter to return...")
            return ""

        print("Current members:")
        system.list_member()
        print("\nSelect owner:")
        for i, m in enumerate(system.members, start=1):
            print(f"{i}. {m.name} (ID: {m.ID})")

        while True:
            choice = input("Choose owner by number: ").strip()
            if not choice.isdigit():
                print("Please enter a number.")
                continue
            idx = int(choice)
            if 1 <= idx <= len(system.members):
                return system.members[idx - 1].ID
            else:
                print("Invalid choice. Try again.")

    def choose_asset_type() -> str:
        """Pick asset type."""
        print("Available asset types:")
        for i, t in enumerate(Asset.ASSET_TYPES, start=1):
            print(f"{i}. {t}")
        while True:
            choice = input("Choose type by number: ").strip()
            if not choice.isdigit():
                print("Please enter a number.")
                continue
            idx = int(choice)
            if 1 <= idx <= len(Asset.ASSET_TYPES):
                return Asset.ASSET_TYPES[idx - 1]
            else:
                print("Invalid choice. Try again.")

    def print_asset_table():
        """Show a brief asset list at top of menu."""
        if len(registry) == 0:
            print("(No assets yet.)")
            return
        df = registry.to_dataframe()
        cols = ["Asset ID", "Name", "Type", "Owner", "Value_Display"]
        cols = [c for c in cols if c in df.columns]
        print(df[cols].to_string(index=False))

    while True:
        clear_screen()
        time.sleep(0.05)
        print("=== Property / Asset Editor ===")
        print(f"Household: {system.household_name}")
        print(f"Total assets: {len(registry)}")
        print("------------------------------")
        print_asset_table()
        print("------------------------------")
        print("1. Add new asset")
        print("2. Edit existing asset")
        print("3. Delete asset")
        print("4. Reports & analysis")
        print("5. Back to main menu")
        print("------------------------------")
        choice = input("Choose an option (1-5): ").strip()

        # 1. add
        if choice == "1":
            clear_screen()
            print("=== Add New Asset ===")
            time.sleep(0.05)

            name = input("Asset name: ").strip()
            if not name:
                print("Name cannot be empty.")
                input("Press Enter to return...")
                continue

            value_str = input("Current value: ").strip()
            try:
                current_value = float(value_str)
            except ValueError:
                print("Invalid value.")
                input("Press Enter to return...")
                continue

            asset_type = choose_asset_type()
            owner_id = choose_owner_id()
            if not owner_id:
                continue

            date_str = input("Date acquired (YYYY-MM-DD, blank for today): ").strip()
            date_acquired = date_str or None

            system.add_asset_for_member(
                member_id=owner_id,
                name=name,
                asset_type=asset_type,
                current_value=current_value,
                date_acquired=date_acquired,
            )
            input("Press Enter to return...")

        # 2. edit
        elif choice == "2":
            clear_screen()
            print("=== Edit Asset ===")
            time.sleep(0.05)

            asset_id = input("Enter Asset ID to edit: ").strip()
            asset = registry._find_asset(asset_id)
            if asset is None:
                print(f"No asset found with ID {asset_id}.")
                input("Press Enter to return...")
                continue

            while True:
                clear_screen()
                print("=== Edit Asset ===")
                print(asset)
                print("------------------------------")
                print("1. Edit name")
                print("2. Edit current value")
                print("3. Edit type")
                print("4. Edit owner")
                print("5. Back")
                print("------------------------------")
                sub_choice = input("Choose an option (1-5): ").strip()

                if sub_choice == "1":
                    new_name = input("New name: ").strip()
                    if new_name:
                        asset.name = new_name
                        asset.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("Name updated.")
                    else:
                        print("Name not changed.")
                    input("Press Enter to continue...")

                elif sub_choice == "2":
                    val_str = input("New value: ").strip()
                    try:
                        new_val = float(val_str)
                        system.update_asset_value(asset_id, new_val)
                    except ValueError:
                        print("Invalid number. Value not changed.")
                    input("Press Enter to continue...")

                elif sub_choice == "3":
                    new_type = choose_asset_type()
                    asset.asset_type = new_type
                    asset.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print("Type updated.")
                    input("Press Enter to continue...")

                elif sub_choice == "4":
                    new_owner_id = choose_owner_id()
                    if new_owner_id:
                        asset.owner = new_owner_id
                        asset.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print("Owner updated.")
                    else:
                        print("Owner not changed.")
                    input("Press Enter to continue...")

                elif sub_choice == "5":
                    break

                else:
                    print("Invalid choice.")
                    input("Press Enter to continue...")

        # 3. delete
        elif choice == "3":
            clear_screen()
            print("=== Delete Asset ===")
            time.sleep(0.05)
            asset_id = input("Enter Asset ID to delete: ").strip()
            confirm = input(f"Are you sure to delete {asset_id}? (y/N): ").strip().lower()
            if confirm == "y":
                system.delete_asset(asset_id)
            else:
                print("Cancelled.")
            input("Press Enter to return...")

        # 4. reports & analysis (list + summary + search + visualization)
        elif choice == "4":
            while True:
                clear_screen()
                print("=== Asset Reports & Analysis ===")
                time.sleep(0.05)
                print("1. List all assets")
                print("2. Asset summary")
                print("3. Search assets")
                print("4. Visualization data")
                print("5. Back")
                print("------------------------------")
                sub = input("Choose an option (1-5): ").strip()

                # 1. list all assets
                if sub == "1":
                    clear_screen()
                    print("=== Asset List ===")
                    time.sleep(0.05)
                    system.list_assets()
                    input("\nPress Enter to return...")

                # 2. summary
                elif sub == "2":
                    clear_screen()
                    print("=== Asset Summary ===")
                    time.sleep(0.05)
                    summary = system.summarize_assets()
                    total = summary.get("Total Value", 0.0)
                    table = summary.get("Summary Table")

                    print(f"Total asset value: ${total:,.2f}")
                    print("\nSummary by Type and Owner:")
                    if table is not None and not table.empty:
                        print(table.to_string(index=False))
                    else:
                        print("No data.")
                    input("\nPress Enter to return...")

                # 3. search
                elif sub == "3":
                    clear_screen()
                    print("=== Search Assets ===")
                    time.sleep(0.05)
                    keyword = input("Enter keyword (ID / name / type / owner): ").strip()
                    df = system.search_assets(keyword)
                    if df is not None and not df.empty:
                        print(df.to_string(index=False))
                    else:
                        print("No matching assets found.")
                    input("\nPress Enter to return...")

                # 4. visualization
                elif sub == "4":
                    clear_screen()
                    print("=== Asset Visualization Data ===")
                    time.sleep(0.05)
                    print("Group by:")
                    print("1. Type")
                    print("2. Owner")
                    gb_choice = input("Choose (1/2): ").strip()
                    if gb_choice == "1":
                        group_by = "Type"
                    elif gb_choice == "2":
                        group_by = "Owner"
                    else:
                        print("Invalid choice.")
                        input("Press Enter to return...")
                        continue

                    df = system.get_asset_visualization_data(group_by=group_by)
                    if df is not None and not df.empty:
                        print(df.to_string(index=False))
                    else:
                        print("No data available.")
                    input("\nPress Enter to return...")

                elif sub == "5":
                    break

                else:
                    print("Invalid choice.")
                    input("Press Enter to try again...")

        # 5. back
        elif choice == "5":
            break

        else:
            print("Invalid choice.")
            input("Press Enter to try again...")
