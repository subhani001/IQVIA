from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.emails import EmailModel
from db import db

_email_parser = reqparse.RequestParser()
_email_parser.add_argument('email_address',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_email_parser.add_argument('contacts_username',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
class Email(Resource):
    # @jwt_required()
    def get(self, email_address):
        email = EmailModel.find_by_email_address(email_address)
        if email:
            return email.json()
        else:
            return {'message': 'Email not found'}, 404

    def delete(self, email_address):
        email = EmailModel.find_by_email_address(email_address)
        if email:
            email.delete_from_db()
            return {'message': 'Email deleted.'}
        else:
            return {'message': 'Email not found.'}, 404

class EmailList(Resource):
    def get(self):
        return {'Emails': list(map(lambda x: x.json(), EmailModel.query.all()))}

class EmailCreate(Resource):
    def post(self):
        data = _email_parser.parse_args()
        if EmailModel.find_by_email_address(data["email_address"]):
            return {'message': "An email with email_address '{}' already exists.".format(data["email_address"])}, 400
        else:
            email = EmailModel(data["email_address"],data["contacts_username"])
            try:
                email.save_to_db()
                return {"message": "Email created successfully."}, 201
            except:
                return {"message": "An error occurred creating the new email."}, 404


class EmailUpdate(Resource):
    def put(self):
        data = _email_parser.parse_args()
        if EmailModel.find_by_email_address(data["email_address"]):
            try:
                email=EmailModel.find_by_email_address(data["email_address"])
                email.email_address=data["email_address"]
                email.contacts_username=data["contacts_username"]
                print(email)
                print(email.email_address,email.contacts_username)
                db.session.commit()
                return {"message": "Email updated successfully."}, 201
            except:
                return {"message": "Error while updating the email"}, 404
        else:
                return {"message": "Sorry there is no email:'{}' exists to update.".format(data["email_address"])}, 404
