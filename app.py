from flask import Flask, jsonify,request
from flask_restful import Api
import redis
from rq import Queue
import time
from resources.emails import Email,EmailList,EmailCreate,EmailUpdate
from resources.contacts import Contact,ContactList,ContactCreate,ContactUpdate,ContacRandom
from flask_sqlalchemy import SQLAlchemy
from models.contacts import ContactModel
import os
from db import db
from celery import Celery
from datetime import timedelta
import random
import datetime

# Initialize Flask app
flask_app = Flask(__name__)

# Flask configuration to integrate SQLAlchemy
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
flask_app.config['PROPAGATE_EXCEPTIONS'] = True

# Flask configuration to integrate CELERY
flask_app.config.update(
    # CELERY_BROKER_URL='redis://localhost:6379/0',
    # CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)

# Initialize DB with flask_app
db.init_app(flask_app)

# Initialize Redis Queue
q=Queue(connection=redis.Redis())

# Define celery app
def make_celery(app):
    celery = Celery(
        app.import_name,
        # backend=app.config['CELERY_RESULT_BACKEND'],
        # broker=app.config['CELERY_BROKER_URL']
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Celery App
celeryapp = make_celery(flask_app)

# running background task throigh celery
@celeryapp.task()
def my_background_task():
        delay=15
        next_time = time.time() + delay
        while True:
            time.sleep(max(0, next_time - time.time()))
            username =''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(10)])
            firstname=''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(20)])
            lastname =''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(20)])
            recordtime=str(datetime.datetime.now()).split('.')[0]
            next_time += (time.time() - next_time) // delay * delay + delay

            # Adding a record for every 15 secods
            if ContactModel.find_by_username(username):
                # return {'message': "A contact with username '{}' already exists.".format(username)}, 400
                print("message: A contact with username '{}' already exists.".format(username))
            else:
                contact = ContactModel(username,firstname,lastname,recordtime)
                try:
                    contact.save_to_db()
                    # return {"message": "Contact created successfully."}, 201
                    print("message: Contact created successfully.")
                except:
                    print("message: Error occured while inserting new contact")
                    # return {"message": "Error occured while inserting new contact "}, 404

            #Delete a record if it is created earlier than 1 min
            # contacts={list(map(lambda x: x.json(), ContactModel.query.all()))}

            contacts=list(map(lambda x: x.json(), ContactModel.query.all()))
            print(contacts)
            for rec in contacts:
                print(rec,type(rec))
                recordtime_dt=datetime.datetime.strptime(rec["recordtime"],'%Y-%m-%d %H:%M:%S')
                timegap=int((datetime.datetime.now()-recordtime_dt).total_seconds())
                if timegap>60:
                    contact  = ContactModel.query.filter_by(username=rec["username"]).first()
                    contact.delete_from_db()
                    # return {'message': 'contact deleted'}
                    print('message: contact deleted')

@flask_app.route("/task")
def index():
    try:
        # job = q.enqueue(my_background_task)
        result=my_background_task.delay()
        print(result)
        # my_background_task.apply_async(queue='high_priority', priority=9)
        # print(result.wait())
        return "Background task started"
        # return f"Task ({job.id}) added to queue at {job.enqueued_at}"
    except:
        return "Error: Background task not started"
#
# CELERYBEAT_SCHEDULE = {
#         'run-every-1-minute': {
#             'task': 'app.my_background_task',
#             'schedule': timedelta(seconds=60)
#         },
#     }

# Start actions
flask_app.app_context().push()
db.create_all()

# API End points
api = Api(flask_app)
api.add_resource(Contact, '/contact/<string:username>')
api.add_resource(ContactList, '/contacts')
api.add_resource(ContactCreate, '/contact/create')
api.add_resource(ContactUpdate, '/contact/update')

api.add_resource(Email, '/email/<string:email_address>')
api.add_resource(EmailList, '/emails')
api.add_resource(EmailCreate, '/email/create')
api.add_resource(EmailUpdate, '/email/update')

if __name__ == '__main__':
    flask_app.run(port=5000, debug=False)
    celeryapp.init_app(flask_app)
