# Most of the final API tests we perform throigh API endpoints using Postman API.
# Here we are doing internal test cases to check quality of functions we developed.

import pytest
from resources import contacts,emails

@pytest.fixtures(scope='module')
def db():
    print('------------setup-------------')
    db=Email()
    # db.connect('data.json')
    yield db
    print('------------teardown----------')
    db.close()

def test_email(db):
    email1=db.get('subhani001@gmail.com')
    asset email1['email_address']=='subhani001@gmail.com'
