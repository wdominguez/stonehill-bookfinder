class Book:
    def __init__(self, title, author, subject, courseId, condition, price, seller, email):
        self.title = title
        self.author = author
        self.subject = subject
        self.courseId = courseId
        self.condition = condition
        self.price = price
        self.seller = seller
        self.email = email

    def toString(self):
        return self.title + " " + self.author + " " + self.subject + " " + self.courseId + " " + self.condition + " " + self.price + " " + self.seller + " " + self.email
