class User:
    def __init__(self, userid, password, email):
        self.userid = userid
        self.password = password
        self.email = email

    def toString(self):
        return self.userid + " " + self.password + " " + self.email
