
from db import db

class EmailModel(db.Model):
    __tablename__ = 'emails'
    email_address = db.Column(db.String(80),primary_key=True)

    contacts= db.relationship('ContactModel')
    contacts_username = db.Column(db.String(80), db.ForeignKey('contacts.username'))

    def __init__(self, email_address,contacts_username ):
        self.email_address = email_address
        self.contacts_username=contacts_username

    def json(self):
        return {'email_address': self.email_address}

    @classmethod
    def find_by_email_address(cls, email_address):
        return cls.query.filter_by(email_address=email_address).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
