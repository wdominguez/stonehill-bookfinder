from userdao import UserDao
from user import User
from bookdao import BookDao
from book import Book
import os
import logging
from passlib.hash import sha256_crypt

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)10s() ] %(message)s"
logging.basicConfig(filename='output.log',format=FORMAT)
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

os.remove('userstable.db')
dao = UserDao()
dao.populate()
users = dao.selectAll()
for user in users:
    print(user.toString())

os.remove('books.db')
dao = BookDao()
dao.populate()
books = dao.selectAll()
for book in books:
    print (book.toString())
