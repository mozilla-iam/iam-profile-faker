import os
from tinydb import TinyDB

from flask import Flask
from flask_restful import Resource, Api

from iam_profile_faker import V2ProfileFactory


app = Flask(__name__)
api = Api(app)


class RandomUsers(Resource):
    """Return users from the profile faker."""

    def get(self, count=100):
        factory = V2ProfileFactory()
        return factory.create_batch(count)


class RandomUser(Resource):
    """Return a single user."""

    def get(self):
        return V2ProfileFactory().create()


def _load_db():
    """Load the saved db file."""
    path = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(path):
        if file.endswith('.json'):
            return os.path.join(path, file)


class PersistentUsers(Resource):
    """Return users stored in a file."""

    def get(self):
        """Return all the users from the db."""
        db = TinyDB(_load_db())
        return db.all()


class PersistentUser(Resource):
    """Return a single user."""

    def get(self, user_id):
        """Return a single user with id `user_id`."""
        db = TinyDB(_load_db())
        return db.all()[user_id]


api.add_resource(RandomUsers, '/', '/users')
api.add_resource(RandomUser, '/user')
api.add_resource(PersistentUsers, '/persistent/users')
api.add_resource(PersistentUser, '/persistent/user/<int:user_id>')


def main():
    app.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    main()
