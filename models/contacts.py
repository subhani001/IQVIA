
from db import db

class ContactModel(db.Model):
    __tablename__ = 'contacts'

    username = db.Column(db.String(80),primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    recordtime=db.Column(db.String(19))

    emails= db.relationship('EmailModel', lazy='dynamic')

    def __init__(self, username, firstname,lastname,recordtime):
        self.username = username
        self.firstname = firstname
        self.lastname=lastname
        self.recordtime=recordtime

    def json(self):
        return {'username': self.username,'firstname': self.firstname,'lastname': self.lastname, 'recordtime':self.recordtime,'emails': [email.json() for email in self.emails.all()]}

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
