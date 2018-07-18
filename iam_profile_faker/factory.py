import json
import random

from faker import Faker


def wrap_metadata_signature(obj, value):
    """Wrap profile value with metadata/signature"""

    # Value key varies based on the type of the value
    if isinstance(value, dict) or isinstance(value, list):
        value_key = 'values'
    else:
        value_key = 'value'

    return {
        value_key: value,
        'metadata': obj.metadata(),
        'signature': obj.signature()
    }


def decorate_metadata_signature(fun):
    """Decorate faker classes to wrap results with metadata/signature."""
    def wrapper(*args, **kwargs):
        value = fun(*args, **kwargs)
        return wrap_metadata_signature(args[0], value)
    return wrapper


class IAMFaker(object):
    def __init__(self, locale=None):
        self.fake = Faker(locale)

    def schema(self):
        """Profile v2 schema faker."""
        return 'https://person-api.sso.mozilla.com/schema/v2/profile'

    def metadata(self):
        """Generate field metadata"""

        classifications = [
            'MOZILLA CONFIDENTIAL',
            'WORKGROUP CONFIDENTIAL: STAFF ONLY',
            'PUBLIC',
            'INDIVIDUAL CONFIDENTIAL'
        ]
        publisher_authority = [
            'access_provider', 'ldap', 'hris', 'cis', 'mozilliansorg'
        ]
        created = self.fake.date_time()
        last_modified = self.fake.date_time_between_dates(datetime_start=created)

        return {
            'classification': random.choice(classifications),
            'last_modified': last_modified.isoformat(),
            'created': created.isoformat(),
            'publisher_authority': random.choice(publisher_authority),
            'verified': self.fake.pybool()
        }

    def signature(self):
        """Generate field signature"""

        def _gen_signature():
            return {
                'alg': 'RS256',
                'typ': 'JWT',
                'value': '{}.{}.{}'.format(self.fake.pystr(), self.fake.pystr(), self.fake.pystr())
            }

        return {
            'publisher': _gen_signature(),
            'additional': [_gen_signature() for i in range(random.randint(0, 5))]
        }

    @decorate_metadata_signature
    def login_method(self):
        """Profile v2 login_method faker."""
        login_methods = [
            'email', 'github', 'google-oauth2', 'ad|Mozilla-LDAP', 'oauth2|firefoxaccounts'
        ]
        return random.choice(login_methods)

    @decorate_metadata_signature
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
                if uid.startswith(login_method['value']):
                    return uid

        return random.choice(user_ids)

    @decorate_metadata_signature
    def usernames(self):
        """Profile v2 usernames faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.user_name()

        return values

    @decorate_metadata_signature
    def identities(self):
        """Profile v2 identities faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.uri()

        return values

    @decorate_metadata_signature
    def ssh_public_keys(self):
        """Profile v2 public SSH key faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            content = self.fake.pystr(min_chars=250, max_chars=500)
            email = self.fake.email()
            values[self.fake.slug()] = 'ssh-rsa {} {}'.format(content, email)

        return values

    @decorate_metadata_signature
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
        for publisher in ['ldap', 'mozilliansorg', 'hris', 'access_provider']:
            v = {}
            for _ in range(random.randint(1, 5)):
                v[self.fake.slug()] = self.fake.pybool()

            values[publisher] = wrap_metadata_signature(self, v)

        return values

    @decorate_metadata_signature
    def office_location(self):
        """Profile v2 office location faker."""
        locations = [
            'Berlin', 'Paris', 'London', 'Toronto', 'Mountain View',
            'San Francisco', 'Vancouver', 'Portland', 'Beijing', 'Taipei'
        ]

        return random.choice(locations)

    @decorate_metadata_signature
    def preferred_languages(self):
        """Profile v2 preferred languages faker."""
        values = []
        for _ in range(random.randint(0, 5)):
            values.append(self.fake.language_code())

        return values

    @decorate_metadata_signature
    def pronouns(self):
        """Profile v2 pronouns faker."""
        return random.choice([None, 'he/him', 'she/her', 'they/them'])

    @decorate_metadata_signature
    def uris(self):
        """Profile v2 URIs faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.uri()

        return values

    @decorate_metadata_signature
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
            'schema': self.schema(),
            'login_method': login_method,
            'user_id': self.user_id(login_method=login_method),
            'active': wrap_metadata_signature(self, self.fake.pybool()),
            'last_modified': wrap_metadata_signature(self, last_modified.isoformat()),
            'created': wrap_metadata_signature(self, created.isoformat()),
            'usernames': self.usernames(),
            'first_name': wrap_metadata_signature(self, self.fake.first_name()),
            'last_name': wrap_metadata_signature(self, self.fake.last_name()),
            'primary_email': wrap_metadata_signature(self, self.fake.email()),
            'identities': self.identities(),
            'ssh_public_keys': self.ssh_public_keys(),
            'pgp_public_keys': self.pgp_public_keys(),
            'access_information': self.access_level(),
            'fun_title': wrap_metadata_signature(self, self.fake.sentence()),
            'description': wrap_metadata_signature(self, self.fake.paragraph()),
            'location_preference': wrap_metadata_signature(self, self.fake.country()),
            'office_location': self.office_location(),
            'timezone': wrap_metadata_signature(self, self.fake.timezone()),
            'preferred_languages': self.preferred_languages(),
            'tags': wrap_metadata_signature(self, self.fake.words()),
            'pronouns': self.pronouns(),
            'picture': wrap_metadata_signature(self, self.fake.image_url()),
            'uris': self.uris(),
            'phone_numbers': self.phone_numbers(),
            'alternative_name': wrap_metadata_signature(self, self.fake.name())
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
