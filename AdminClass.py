class Admin():
    def __init__(self):
        self.name = "John"
        self.password = "1234"

    def login(self,name,password):
        if name == self.name and password == self.password:
            return True
        else:
            return False