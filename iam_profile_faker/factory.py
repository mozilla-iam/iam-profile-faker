import json
import random

from faker import Faker


class IAMFaker(object):
    def __init__(self, locale=None):
        self.fake = Faker(locale)

    def schema(self):
        """Profile v2 schema faker."""
        return 'https://person-api.sso.mozilla.com/schema/v2/profile'

    def login_method(self):
        """Profile v2 login_method faker."""
        login_methods = [
            'email', 'github', 'google-oauth2', 'ad|Mozilla-LDAP', 'oauth2|firefoxaccounts'
        ]
        return random.choice(login_methods)

    def user_id(self, login_method=None):
        """Profile v2 user_id attribute faker."""
        user_ids = [
            'email|{}'.format(self.fake.pystr(min_chars=24, max_chars=24)),
            'github|{}'.format(self.fake.pyint()),
            'google-oauth2|{}'.format(self.fake.pyint()),
            'ad|Mozilla-LDAP|{}'.format(self.fake.user_name()),
            'oauth2|firefoxaccounts|{}'.format(self.fake.pystr(min_chars=32, max_chars=32))
        ]

        if login_method:
            for uid in user_ids:
                if uid.startswith(login_method):
                    return uid

        return random.choice(user_ids)

    def usernames(self):
        """Profile v2 usernames faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.user_name()

        return values

    def identities(self):
        """Profile v2 identities faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.uri()

        return values

    def ssh_public_keys(self):
        """Profile v2 public SSH key faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            content = self.fake.pystr(min_chars=250, max_chars=500)
            email = self.fake.email()
            values[self.fake.slug()] = 'ssh-rsa {} {}'.format(content, email)

        return values

    def pgp_public_keys(self):
        """Profile v2 public PGP key faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            pgp_key = '-----BEGIN PGP PUBLIC KEY BLOCK-----\n\n'
            pgp_key += self.fake.pystr(min_chars=250, max_chars=500)
            pgp_key += '\n-----END PGP PUBLIC KEY BLOCK-----\n'
            values[self.fake.slug()] = pgp_key

        return values

    def access_level(self):
        """Profile v2 access level faker."""
        values = {}
        for publisher in ['ldap', 'mozilliansorg']:
            values[publisher] = {}
            for _ in range(random.randint(0, 5)):
                values[publisher][self.fake.slug()] = self.fake.pybool()

        return values

    def office_location(self):
        """Profile v2 office location faker."""
        locations = [
            'Berlin', 'Paris', 'London', 'Toronto', 'Mountain View',
            'San Francisco', 'Vancouver', 'Portland', 'Beijing', 'Taipei'
        ]

        return random.choice(locations)

    def preferred_languages(self):
        """Profile v2 preferred languages faker."""
        values = []
        for _ in range(random.randint(0, 5)):
            values.append(self.fake.language_code())

        return values

    def pronouns(self):
        """Profile v2 pronouns faker."""
        return random.choice([None, 'he/him', 'she/her', 'they/them'])

    def uris(self):
        """Profile v2 URIs faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.uri()

        return values

    def phone_numbers(self):
        """Profile v2 phone_numbers faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.phone_number()

        return values

    def create(self):
        """Method to generate fake profile v2 objects."""
        login_method = self.login_method()
        created = self.fake.date_time()
        last_modified = self.fake.date_time_between_dates(datetime_start=created)

        obj = {
            '$schema': self.schema(),
            'login_method': login_method,
            'user_id': self.user_id(login_method=login_method),
            'active': self.fake.pybool(),
            'last_modified': last_modified.isoformat(),
            'created': created.isoformat(),
            'usernames': self.usernames(),
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'primary_email': self.fake.email(),
            'identities': self.identities(),
            'ssh_public_keys': self.ssh_public_keys(),
            'pgp_public_keys': self.pgp_public_keys(),
            'access_information': self.access_level(),
            'fun_title': self.fake.sentence(),
            'description': self.fake.paragraph(),
            'location_preference': self.fake.country(),
            'office_location': self.office_location(),
            'timezone': self.fake.timezone(),
            'preferred_languages': self.preferred_languages(),
            'tags': self.fake.words(),
            'pronouns': self.pronouns(),
            'picture': self.fake.image_url(),
            'uris': self.uris(),
            'phone_numbers': self.phone_numbers(),
            'alternative_name': self.fake.name()
        }

        return obj


class V2ProfileFactory(object):
    def create(self, export_json=False):
        """Generate fake profile v2 object."""
        faker = IAMFaker()
        output = faker.create()

        if export_json:
            return json.dumps(output)
        return output

    def create_batch(self, count, export_json=False):
        """Generate batch fake profile v2 objects."""
        faker = IAMFaker()
        batch = []
        for _ in range(count):
            obj = faker.create()
            batch.append(obj)

        if export_json:
            return json.dumps(batch)
        return batch
