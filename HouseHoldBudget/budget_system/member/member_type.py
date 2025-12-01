from .member import member


class dependant(member):
    def __init__(self,name,ID,DOB):
        super().__init__(name,ID,DOB)
        self.type='dependant'
    def __str__(self):
        return f"{self.name} (ID: {self.ID}, Dependant)"


class guardian(member):
    def __init__(self,name,ID,DOB,income,job_title=''):
        super().__init__(name,ID,DOB)
        self.type='guardian'
        self.income=income
        self.job_title=job_title
    def new_job(self,job):
        self.job_title=job
    def new_income(self,income):
        self.income=income
    def get_income(self):
        return self.income
    def __str__(self):
        return f"{self.name} (ID: {self.ID}, Guardian, Income: {self.income}, Job: {self.job_title})"

def member_edit(member_obj):
    print(f"Current member type: {member_obj.type}")

    while True:
        print("\n--- Member Editor ---")
        if member_obj.type == 'dependant':
            print("1. Edit name")
            print("2. Edit date of birth (DOB)")
            print("3. Exit editor")

            choice = input("Please select the information to edit (1,2,3): ")

            if choice == '3':
                print("Exiting member editor.")
                break

            elif choice == '1':
                new_name = input('Please enter a new name: ')
                member_obj.new_name(new_name)
                print("Name has been updated.")

            elif choice == '2':
                new_DOB = input('Please enter a new date of birth (YYYY-MM-DD): ')
                member_obj.new_DOB(new_DOB)
                print("Date of birth has been updated.")

            else:
                print("Invalid choice. Please try again.")

        elif member_obj.type == 'guardian':
            print("1. Edit name")
            print("2. Edit date of birth (DOB)")
            print("3. Edit job")
            print("4. Edit income")
            print("5. Exit editor")

            choice = input("Please select the information to edit (1-5): ")

            if choice == '5':
                print("Exiting member editor.")
                break

            elif choice == '1':
                new_name = input('Please enter a new name: ')
                member_obj.new_name(new_name)
                print("Name has been updated.")

            elif choice == '2':
                new_DOB = input('Please enter a new date of birth (YYYY-MM-DD): ')
                member_obj.new_DOB(new_DOB)
                print("Date of birth has been updated.")

            elif choice == '3':
                new_job = input('Please enter a new job: ')
                new_income = float(input('Please enter the new income associated with this job: '))
                member_obj.new_job(new_job)
                member_obj.new_income(new_income)
                print("Job and income have been updated.")

            elif choice == '4':
                new_income = float(input('Please enter the new income: '))
                member_obj.new_income(new_income)
                print("Income has been updated.")

            else:
                print("Invalid choice. Please try again.")

        else:
            print("Unknown member type. Exiting editor.")
            break