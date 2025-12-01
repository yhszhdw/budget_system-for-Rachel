from datetime import datetime

class member:
    def __init__(self,name,ID,DOB):
        self.name=name
        self.DOB=DOB
        self.ID=ID
    def new_name(self,name):
        self.name=name
    def new_DOB(self,DOB):
        self.DOB=DOB
    def new_ID(self,ID):
        self.ID=ID
    def get_age(self):
    """Return the age of the member in years (approximate)."""
    try:
        birth = datetime.strptime(self.DOB, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except:
        return None