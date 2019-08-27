from flask_jwt_extended import JWTManager
from db import db
from models.contacts import ContactModel
from flask_restful import Resource, reqparse
import time
import random
import datetime

_contact_parser = reqparse.RequestParser()
_contact_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_contact_parser.add_argument('firstname',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

_contact_parser.add_argument('lastname',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
class Contact(Resource):
    def get(self, username):
        contact = ContactModel.find_by_username(username)
        if contact:
            return contact.json()
        else:
            return {'message': 'contact not found'}, 404

    def delete(self, username):
        contact = ContactModel.find_by_username(username)
        if contact:
            contact.delete_from_db()
            return {'message': 'contact deleted'}
        else:
            return {'message': 'contact not found'}

class ContactCreate(Resource):
    def post(self):
        data = _contact_parser.parse_args()
        if ContactModel.find_by_username(data["username"]):
            return {'message': "A contact with username '{}' already exists.".format(data["username"])}, 400
        else:
            recordtime=str(datetime.datetime.now()).split('.')[0]
            contact = ContactModel(data["username"],data["firstname"],data["lastname"],recordtime)
            try:
                contact.save_to_db()
                return {"message": "Contact created successfully."}, 201
            except:
                return {"message": "Error occured while inserting new contact "}, 404


class ContactUpdate(Resource):
    def put(self):
        data = _contact_parser.parse_args()
        x=ContactModel.find_by_username(data["username"])
        print("x",x)
        if ContactModel.find_by_username(data["username"]):
            try:
                contact=ContactModel.find_by_username(data["username"])
                contact.username=data["username"]
                contact.firstname=data["firstname"]
                contact.lastname=data["lastname"]
                contact.recordtime=str(datetime.datetime.now()).split('.')[0]
                db.session.commit()
                return {"message": "Contact updated successfully."}, 201
            except:
                return {"message": "Error while updating the Contact"}, 404
        return {"message": "Sorry there is no contact with this username to update."}, 404


class ContactList(Resource):
    def get(self):
        return {'contacts': list(map(lambda x: x.json(), ContactModel.query.all()))}

#
# class ContactDeleteRamdom():
#     @classmethod
#     def delete(self):
#         contacts={list(map(lambda x: x.json(), ContactModel.query.all()))}
#         for rec in contacts:
#             recordtime_dt=datetime.datetime.strptime(rec["recordtime"],'%Y-%m-%d %H:%M:%S')
#             timegap=int((datetime.datetime.now()-recordtime_dt).total_seconds())
#             if timegap>60:
#                 contact.delete_from_db()
#                 return {'message': 'contact deleted'}


class ContacRandom():
    @classmethod
    def randomcreatedelete(self,delay):
        next_time = time.time() + delay
        while True:
            time.sleep(max(0, next_time - time.time()))
            username =''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(10)])
            firstname=''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(20)])
            lastname =''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(20)])
            recordtime=str(datetime.datetime.now()).split('.')[0]
            next_time += (time.time() - next_time) // delay * delay + delay
            print(username,firstname,lastname,recordtime,recordtime_dt)

            # Adding a record for every 15 secods
            if ContactModel.find_by_username(username):
                return {'message': "A contact with username '{}' already exists.".format(username)}, 400
            else:
                contact = ContactModel(username,firstname,lastname,recordtime)
                try:
                    contact.save_to_db()
                    return {"message": "Contact created successfully."}, 201
                except:
                    return {"message": "Error occured while inserting new contact "}, 404

            #Delete a record if it is created earlier than 1 min
            contacts={list(map(lambda x: x.json(), ContactModel.query.all()))}
            for rec in contacts:
                recordtime_dt=datetime.datetime.strptime(rec["recordtime"],'%Y-%m-%d %H:%M:%S')
                timegap=int((datetime.datetime.now()-recordtime_dt).total_seconds())
                if timegap>60:
                    contact.delete_from_db()
                    return {'message': 'contact deleted'}
