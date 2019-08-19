import dataset
from book import Book
from flask import current_app
import logging

class BookDao:
    def __init__(self):
        self.connectString = 'sqlite:///books.db'
        self.db = dataset.connect(self.connectString)
        self.table = self.db['books']
        try:
            self.logger = current_app.logger
        except:
            self.logger = logging.getLogger('root')
        self.logger.debug('got to bookDao')
        
    def rowToBook(self,row):
        book = Book(row['title'], row['author'], row['subject'], row['courseId'], row['condition'], row['price'], row['seller'], row['email'])
        return book

    def bookToRow(self,book):
        row = dict(title=book.title, author=book.author, subject=book.subject, courseId=book.courseId, condition=book.condition, price=book.price, seller=book.seller, email=book.email)
        return row

    def selectByUserid(self, userid):
        rows  = self.table.find(seller=userid)
        result = []
        if (rows is None):
            print('failed to find userid: ', userid)
            result = None
        else:
            for row in rows:
                result.append(self.rowToBook(row))

        return result

    def selectAll(self):
        print("in select all")
        table = self.db['books']
        rows = table.all()
        
        result = []
        print ("before row loop")
        for row in rows:
            print("in row loop")
            result.append(self.rowToBook(row))

        return result
        
    def insert(self,book):
        self.table.insert(self.bookToRow(book))
        self.db.commit()

    def update(self,book):
        self.table.update(self.bookToRow(book),['title'])
        self.db.commit()

    def delete(self, book):
        self.table.delete(title=book.title, seller=book.seller)
        self.db.commit()

    def populate(self):
        self.table.insert(self.bookToRow(Book('Physics for Scientists and Engineers', 'Giancoli', 'Physics', 'PHY 121', 'Fair', '100', 'AceTheSkyhawk', 'askyhawk@stonehill.edu')))
        self.db.commit()
