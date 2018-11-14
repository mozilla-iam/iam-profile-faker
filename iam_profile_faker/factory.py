import itertools
import json
import random

from faker import Faker

C_NDAED = 'MOZILLA CONFIDENTIAL'
C_STAFF = 'WORKGROUP CONFIDENTIAL: STAFF ONLY'
C_GROUP = 'WORKGROUP CONFIDENTIAL'
C_PUBLIC = 'PUBLIC'
C_PRIVATE = 'INDIVIDUAL CONFIDENTIAL'

DISPLAY = [
    'public',
    'authenticated',
    'vouched',
    'ndaed',
    'staff',
    'private'
]


def wrap_metadata_signature(obj, value, display=DISPLAY, c12n=C_GROUP):
    """Wrap profile value with metadata/signature"""

    # Value key varies based on the type of the value
    if isinstance(value, dict) or isinstance(value, list):
        value_key = 'values'
    else:
        value_key = 'value'

    return {
        value_key: value,
        'metadata': obj.metadata(display, c12n),
        'signature': obj.signature()
    }


def decorate_metadata_signature(display=DISPLAY, c12n=C_GROUP):
    def wrap(fun):
        """Decorate faker classes to wrap results with metadata/signature."""
        def wrapper(*args, **kwargs):
            value = fun(*args, **kwargs)
            return wrap_metadata_signature(args[0], value, display, c12n)
        return wrapper
    return wrap


def create_random_hierarchy_iter():
    """Generate hierarchy iterator with a random pattern"""
    def gen():
        for i in itertools.count():
            yield (i + 1, random.randint(0, i))
    return gen()


class IAMFaker(object):
    def __init__(self, locale=None, hierarchy=None):
        self.fake = Faker(locale)
        self.hierarchy = hierarchy

    def get_public_email_address(self):
        value = []
        for _ in range(random.randint(0, 5)):
            value.append(self.fake.email())

        return value

    def schema(self):
        """Profile v2 schema faker."""
        return 'https://person-api.sso.mozilla.com/schema/v2/profile'

    def metadata(self, display=DISPLAY, c12n=C_GROUP):
        """Generate field metadata"""

        created = self.fake.date_time()
        last_modified = self.fake.date_time_between_dates(datetime_start=created)

        return {
            'classification': c12n,
            'display': random.choice(display),
            'last_modified': last_modified.isoformat(),
            'created': created.isoformat(),
            'verified': self.fake.pybool(),
        }

    def signature(self):
        """Generate field signature"""

        def _gen_signature():
            return {
                'alg': 'RS256',
                'typ': 'JWS',
                'value': '{}.{}.{}'.format(self.fake.pystr(), self.fake.pystr(),
                                           self.fake.pystr()),
                'name': random.choice(['access_provider', 'ldap', 'hris', 'cis', 'mozilliansorg'])
            }

        return {
            'publisher': _gen_signature(),
            'additional': [_gen_signature() for i in range(random.randint(0, 5))]
        }

    @decorate_metadata_signature(c12n=C_PUBLIC)
    def login_method(self):
        """Profile v2 login_method faker."""
        login_methods = [
            'email', 'github', 'google-oauth2', 'ad|Mozilla-LDAP', 'oauth2|firefoxaccounts'
        ]
        return random.choice(login_methods)

    @decorate_metadata_signature(c12n=C_PUBLIC)
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

    @decorate_metadata_signature(display=["public"], c12n=C_GROUP)
    def usernames(self):
        """Profile v2 usernames faker."""
        values = {}
        values["mozilliansorg"] = self.fake.user_name()
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.user_name()

        return values

    def identities(self):
        """Profile v2 identities faker."""
        return {
            'github_id_v3': wrap_metadata_signature(self, self.fake.md5()),
            'github_id_v4': wrap_metadata_signature(self, self.fake.md5()),
            'dinopark_id': wrap_metadata_signature(self, self.fake.md5(), display=["public"]),
            'mozilliansorg_id': wrap_metadata_signature(self, self.fake.md5()),
            'bugzilla_mozilla_org_id': wrap_metadata_signature(self, self.fake.md5()),
            'mozilla_ldap_id': wrap_metadata_signature(self, self.fake.md5(), display=["staff"]),
            'mozilla_posix_id': wrap_metadata_signature(self, self.fake.md5()),
            'google_oauth2_id': wrap_metadata_signature(self, self.fake.md5()),
            'firefox_accounts_id': wrap_metadata_signature(self, self.fake.md5()),
        }

    @decorate_metadata_signature(c12n=C_PUBLIC)
    def ssh_public_keys(self):
        """Profile v2 public SSH key faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            content = self.fake.pystr(min_chars=250, max_chars=500)
            email = self.fake.email()
            values[self.fake.slug()] = 'ssh-rsa {} {}'.format(content, email)

        return values

    @decorate_metadata_signature(c12n=C_PUBLIC)
    def pgp_public_keys(self):
        """Profile v2 public PGP key faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            pgp_key = '-----BEGIN PGP PUBLIC KEY BLOCK-----\n\n'
            pgp_key += self.fake.pystr(min_chars=250, max_chars=500)
            pgp_key += '\n-----END PGP PUBLIC KEY BLOCK-----\n'
            values[self.fake.slug()] = pgp_key

        return values

    def access_information(self):
        """Profile v2 access information faker."""
        values = {}
        publishers_c12n = [
            ('ldap', C_PUBLIC),
            ('mozilliansorg', C_PUBLIC),
            ('access_provider', C_GROUP)
        ]
        for (publisher, c12n) in publishers_c12n:
            v = {}
            for _ in range(random.randint(1, 5)):
                if publisher == 'mozilliansorg':
                    v[self.fake.slug()] = None
                else:
                    v[self.fake.slug()] = self.fake.pybool()

            values[publisher] = wrap_metadata_signature(
                self, v, display=[None], c12n=c12n)

        values['hris'] = wrap_metadata_signature(
            self, self.hris(), display=[None], c12n=C_STAFF)

        return values

    def office_location(self):
        """Profile v2 office location faker."""
        locations = [
            'Berlin', 'Paris', 'London', 'Toronto', 'Mountain View',
            'San Francisco', 'Vancouver', 'Portland', 'Beijing', 'Taipei'
        ]

        return random.choice(locations)

    @decorate_metadata_signature()
    def languages(self):
        """Profile v2 preferred languages faker."""
        values = []
        for _ in range(random.randint(0, 5)):
            values.append(self.fake.language_code())

        return values

    @decorate_metadata_signature()
    def pronouns(self):
        """Profile v2 pronouns faker."""
        return random.choice([None, 'he/him', 'she/her', 'they/them'])

    @decorate_metadata_signature()
    def uris(self):
        """Profile v2 URIs faker."""

        # external accounts supported by DinoPark, prefixed with EA#
        external_accounts = [
            "EA#AIM",
            "EA#BITBUCKET",
            "EA#BMO",
            "EA#DISCORD",
            "EA#FACEBOOK",
            "EA#LANYRD",
            "EA#LINKEDIN",
            "EA#MDN",
            "EA#MASTODON",
            "EA#AMO",
            "EA#DISCOURSE",
            "EA#MOZPHAB",
            "EA#MOZILLAPONTOON",
            "EA#REMO",
            "EA#SUMO",
            "EA#WEBMAKER",
            "EA#MOZILLAWIKI",
            "EA#Phone",
            "EA#Phone",
            "EA#SKYPE",
            "EA#SLIDESHARE",
            "EA#TELEGRAM",
            "EA#TRANSIFEX",
            "EA#TWITTER",
            "EA#WEBSITE",
            "EA#JABBER",
            "EA#YAHOO",
        ]

        values = {}
        for name in random.sample(external_accounts, random.randint(0, 4)):
            values[name] = self.fake.uri()
        for _ in range(random.randint(0, 4)):
            values[self.fake.slug()] = self.fake.uri()

        return values

    @decorate_metadata_signature()
    def phone_numbers(self):
        """Profile v2 phone_numbers faker."""
        values = {}
        for _ in range(random.randint(0, 5)):
            values[self.fake.slug()] = self.fake.phone_number()

        return values

    def staff_information(self, hris):
        """ Profile v2 staff information faker"""
        def wrap(value):
            return wrap_metadata_signature(self, value, display=["ndaed"], c12n=C_NDAED)
        return {
            'manager': wrap(hris['IsManager']),
            'director': wrap(hris['isDirectorOrAbove']),
            'staff': wrap(True),
            'title': wrap(hris['businessTitle']),
            'team': wrap(hris['Team']),
            'cost_center': wrap_metadata_signature(self, hris['Cost_Center'],
                                                   display=["staff"],
                                                   c12n=C_STAFF),
            'worker_type': wrap_metadata_signature(self, hris['WorkerType'],
                                                   display=["staff"],
                                                   c12n=C_STAFF),
            'wpr_desk_number': wrap(hris['WPRDeskNumber']),
            'office_location': wrap(hris['Location_Description']),
        }

    def hris(self):
        """Profile v2 HRIS faker"""

        def get_management_level():
            level = random.choice(['Junior', 'Senior', 'Staff'])
            return random.choice(['{} Manager'.format(level), ''])

        employee_id, manager_id = (next(self.hierarchy)
                                   if self.hierarchy
                                   else (self.fake.pyint(), self.fake.pyint()))

        values = {
            'LastName': self.fake.last_name(),
            'Preferred_Name': self.fake.name(),
            'PreferredFirstName': self.fake.first_name(),
            'LegalFirstName': self.fake.first_name(),
            'EmployeeID': employee_id,
            'businessTitle': self.fake.job(),
            'IsManager': self.fake.pybool(),
            'isDirectorOrAbove': self.fake.pybool(),
            'Management_Level': get_management_level(),
            'HireDate': self.fake.date(pattern="%Y-%m-%d", end_datetime=None),
            'CurrentlyActive': random.choice(['0', '1']),
            'Entity': self.fake.company(),
            'Team': '{} team'.format(self.fake.color_name()),
            'Cost_Center': '{} - {}'.format(self.fake.pyint(), self.fake.job()),
            'WorkerType': random.choice(['Employee', 'Seasonal', 'Geocontractor']),
            'Location_Description': random.choice([
                'Berlin', 'Paris', 'London', 'Toronto', 'Mountain View',
                'San Francisco', 'Vancouver', 'Portland', 'Beijing', 'Taipei'
            ]),
            'Time_Zone': self.fake.timezone(),
            'LocationCity': self.fake.city(),
            'LocationState': self.fake.state(),
            'LocationCountryFull': self.fake.country(),
            'LocationCountryISO2': self.fake.country_code(),
            'WorkersManager': 'unknown',
            'WorkersManagersEmployeeID': manager_id,
            'Worker_s_Manager_s_Email_Address': self.fake.email(),
            'primary_work_email': self.fake.email(),
            'WPRDeskNumber': str(self.fake.pyint()),
            'EgenciaPOSCountry': self.fake.country_code(),
            'PublicEmailAddresses': self.get_public_email_address()
        }

        return values

    def create(self):
        """Method to generate fake profile v2 objects."""
        login_method = self.login_method()
        created = self.fake.date_time()
        last_modified = self.fake.date_time_between_dates(datetime_start=created)

        user_id = self.user_id(login_method=login_method)
        user_id["metadata"]["display"] = "public"

        access_information = self.access_information()
        obj = {
            'access_information': access_information,
            'active': wrap_metadata_signature(self, self.fake.pybool(), display=[None]),
            'alternative_name': wrap_metadata_signature(self, self.fake.name()),
            'created': wrap_metadata_signature(self, created.isoformat(), c12n=C_PUBLIC),
            'description': wrap_metadata_signature(self, self.fake.paragraph()),
            'first_name': wrap_metadata_signature(self, self.fake.first_name(), c12n=C_PUBLIC),
            'fun_title': wrap_metadata_signature(self, self.fake.sentence()),
            'identities': self.identities(),
            'languages': self.languages(),
            'last_modified': wrap_metadata_signature(self,
                                                     last_modified.isoformat(),
                                                     c12n=C_PUBLIC),
            'last_name': wrap_metadata_signature(self, self.fake.last_name(), c12n=C_PUBLIC),
            'location': wrap_metadata_signature(self, self.fake.country()),
            'login_method': login_method,
            'pgp_public_keys': self.pgp_public_keys(),
            'phone_numbers': self.phone_numbers(),
            'picture': wrap_metadata_signature(self, None, c12n=C_PUBLIC),
            'primary_email': wrap_metadata_signature(self, self.fake.email(), c12n=C_PUBLIC),
            'pronouns': self.pronouns(),
            'schema': self.schema(),
            'ssh_public_keys': self.ssh_public_keys(),
            'staff_information': self.staff_information(access_information['hris']['values']),
            'tags': wrap_metadata_signature(self, self.fake.words()),
            'timezone': wrap_metadata_signature(self, self.fake.timezone()),
            'uris': self.uris(),
            'user_id': user_id,
            'usernames': self.usernames(),
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
        hierarchy = create_random_hierarchy_iter()
        faker = IAMFaker(hierarchy=hierarchy)
        batch = []
        for _ in range(count):
            obj = faker.create()
            batch.append(obj)

        if export_json:
            return json.dumps(batch)
        return batch
