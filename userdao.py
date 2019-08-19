import dataset
import logging
from user import User
from flask import current_app
from passlib.hash import sha256_crypt

class UserDao:
    def __init__(self):
        self.db = dataset.connect('sqlite:///userstable.db')
        self.table = self.db['userstable']
        try:
            self.logger = current_app.logger
        except:
            self.logger = logging.getLogger('root')
            
        self.logger.debug('got to UserDao')
        
    def rowToUser(self,row):
        user = User(row['userid'], row['password'], row['email'])
        return user

    def userToRow(self,user):
        row = dict(userid=user.userid, password=user.password, email=user.email)
        return row

    def selectByUserid(self,userid):
        self.logger.debug('userid: %r', userid)
        rows = self.table.find(userid=userid)
        self.logger.debug('rows: %r', rows)
        result = None
        self.logger.debug('rows: %r', rows)
        if (rows is None):
            self.logger.debug('in if')
            print('UserDao:selectByUserid failed to find user with ' + userid)
            result = None
        else:
            self.logger.debug('in first else')
            count = 0
            self.logger.debug('asdf')
            for row in rows:
                self.logger.debug('before if')
                if (count > 0):
                    self.logger.debug('more than one user selected')
                    return None
                else:
                    self.logger.debug('in second else')
                    result = self.rowToUser(row)
                    count = count + 1
        self.logger.debug('about to return')
        return result

    def selectAll(self):
        table = self.db['userstable']
        rows = table.all()

        result = []
        for row in rows:
            result.append(self.rowToUser(row))

        return result
        
    def insert(self,user):
        user.password = sha256_crypt.encrypt(user.password)
        print("encrypted pass: ", user.password)
        self.table.insert(self.userToRow(user))
        self.db.commit()

    def update(self,user):
        self.table.update(self.userToRow(user), ['userid'])
        self.db.commit()

    def delete(self,user):
        self.table.delete(userid=userid)
        self.db.commit()

    def populate(self):
        self.table.insert(self.userToRow(User('Wyatt', sha256_crypt.encrypt('pass'), 'wdominguez@students.stonehill.edu')))
        self.table.insert(self.userToRow(User('Maddy', sha256_crypt.encrypt('minniemouse'), 'mhughes3@students.stonehill.edu')))
        self.table.insert(self.userToRow(User('Nora', sha256_crypt.encrypt('trailmix'), 'nmcquilkon@students.stonehill.edu')))
        self.db.commit()
