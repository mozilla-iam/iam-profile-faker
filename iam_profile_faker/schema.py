import json
import graphene
import requests
from aniso8601 import parse_datetime

from tinydb import TinyDB, Query as tinydb_query


# Helper functions
def parse_datetime_iso8601(datetime):
    """Parse a string in ISO8601 format."""
    if not datetime:
        return None

    try:
        dt = parse_datetime(datetime)
    except ValueError:
        return None
    else:
        return dt


def is_json(payload):
    """Check if a payload is valid JSON."""
    try:
        json.loads(payload)
    except (TypeError, ValueError):
        return False
    else:
        return True


class ObjectFactory(dict):
    """Allows to parse a dict structure with an object like notation (attributes)."""

    def __init__(self, data={}):
        super(ObjectFactory, self).__init__()
        for k, v in data.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = ObjectFactory(value)
        super(ObjectFactory, self).__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    __setattr__ = __setitem__


def object_hook(dct):
    """Transform every JSON object to Python objects."""
    return ObjectFactory(dct)


def json2obj(data):
    return json.loads(data, object_hook=object_hook)


class Alg(graphene.Enum):
    """V2 Schema Alg object for Graphene."""

    HS256 = 'HS256'
    RS256 = 'RS256'
    RSA = 'RSA'
    ED25519 = 'ED25519'


class Typ(graphene.Enum):
    """V2 Schema Typ object for Graphene."""

    JWT = 'JWT'
    PGP = 'PGP'


class Classification(graphene.Enum):
    """V2 Schema Classification object for Graphene."""

    MOZILLA_CONFIDENTIAL = 'MOZILLA CONFIDENTIAL'
    STAFF_ONLY = 'STAFF ONLY'
    NDA = 'NDA'
    REGISTERED = 'REGISTERED'
    PUBLIC = 'PUBLIC'


class PublisherAuthority(graphene.Enum):
    """V2 Schema PublisherAuthority object for Graphene."""

    LDAP = 'ldap'
    MOZILLIANS = 'mozilliansorg'
    HRIS = 'hris'
    CIS = 'cis'
    ACCESS_PROVIDER = 'access_provider'


class Publisher(graphene.ObjectType):
    """V2 Schema Publisher object for Graphene."""

    alg = graphene.Field(Alg)
    typ = graphene.Field(Typ)
    value = graphene.String()


class Signature(graphene.ObjectType):
    """V2 Schema Signature object for Graphene."""

    publisher = graphene.Field(Publisher)
    additional = graphene.List(Publisher)


class Metadata(graphene.ObjectType):
    """V2 Schema Metadata object for Graphene."""

    classification = graphene.Field(Classification)
    last_modified = graphene.DateTime()
    created = graphene.DateTime()
    publisher_authority = graphene.Field(PublisherAuthority)
    verified = graphene.Boolean()

    def resolve_last_modified(self, info, **kwargs):
        """Resolver to return a datetime object."""
        return parse_datetime_iso8601(self.get('last_modified'))

    def resolve_created(self, info, **kwargs):
        """Resolver to return a datetime object."""
        return parse_datetime_iso8601(self.get('created'))


class StandardAttributeDatetime(graphene.ObjectType):
    """V2 Schema StandardAttributeDatetime object for Graphene."""

    value = graphene.DateTime()
    signature = graphene.Field(Signature)
    metadata = graphene.Field(Metadata)

    def resolve_value(self, info, **kwargs):
        """Resolver to return a datetime object."""
        return parse_datetime_iso8601(self.get('value'))


class StandardAttributeBoolean(graphene.ObjectType):
    """V2 Schema StandardAttributeBoolean object for Graphene."""

    value = graphene.Boolean()
    signature = graphene.Field(Signature)
    metadata = graphene.Field(Metadata)


class StandardAttributeString(graphene.ObjectType):
    """V2 Schema StandardAttributeString object for Graphene."""

    value = graphene.String()
    signature = graphene.Field(Signature)
    metadata = graphene.Field(Metadata)


class IdentitiesValues(graphene.ObjectType):
    """V2 Schema IdentitiesValues object for Graphene."""

    github_id_v3 = graphene.String()
    github_id_v4 = graphene.String()
    LDAP = graphene.String()
    bugzilla = graphene.String()
    google = graphene.String()
    firefoxaccounts = graphene.String()
    emails = graphene.List(graphene.String)

    def resolve_bugzilla(self, info, **kwargs):
        """Custom resolver for the Bugzilla Identity.

        Extract the bugzilla.mozilla.org Identity from the profile v2 schema.
        """
        return self.get('bugzilla.mozilla.org')

    def resolve_google(self, info, **kwargs):
        """Custom resolver for the Google Identity.

        Extract the google-oauth2 Identity from the profile v2 schema.
        """
        return self.get('google-oauth2')


class Identities(graphene.ObjectType):
    """V2 Schema Identities object for Graphene."""

    values = graphene.Field(IdentitiesValues)
    signature = graphene.Field(Signature)
    metadata = graphene.Field(Metadata)

    def resolve_values(self, info, **kwargs):
        return self.get('values')


class StandardAttributeValues(graphene.ObjectType):
    """V2 Schema StandardAttributeValues object for Graphene."""

    values = graphene.List(graphene.String)
    metadata = graphene.Field(Metadata)
    signature = graphene.Field(Signature)

    def resolve_values(self, info, **kwargs):
        """Custom resolver for the list of values."""
        if isinstance(self['values'], list):
            return self['values']
        values = self.get('values')
        if values:
            return values.items()
        return None


class AccessInformation(graphene.ObjectType):
    """V2 Schema AccessInformation object for Graphene."""

    ldap = graphene.Field(StandardAttributeValues)
    mozilliansorg = graphene.Field(StandardAttributeValues)
    hris = graphene.Field(StandardAttributeValues)
    access_provider = graphene.Field(StandardAttributeValues)


class CoreProfile(graphene.ObjectType):
    """V2 Schema CoreProfile object for Graphene."""

    user_id = graphene.Field(StandardAttributeString)
    login_method = graphene.Field(StandardAttributeString)
    active = graphene.Field(StandardAttributeBoolean)
    last_modified = graphene.Field(StandardAttributeDatetime)
    created = graphene.Field(StandardAttributeDatetime)
    usernames = graphene.Field(StandardAttributeValues)
    first_name = graphene.Field(StandardAttributeString)
    last_name = graphene.Field(StandardAttributeString)
    primary_email = graphene.Field(StandardAttributeString)
    identities = graphene.Field(Identities)
    ssh_public_keys = graphene.Field(StandardAttributeValues)
    pgp_public_keys = graphene.Field(StandardAttributeValues)
    access_information = graphene.Field(AccessInformation)
    fun_title = graphene.Field(StandardAttributeString)
    description = graphene.Field(StandardAttributeString)
    location_preference = graphene.Field(StandardAttributeString)
    office_location = graphene.Field(StandardAttributeString)
    timezone = graphene.Field(StandardAttributeString)
    preferred_language = graphene.Field(StandardAttributeValues)
    tags = graphene.Field(StandardAttributeValues)
    pronouns = graphene.Field(StandardAttributeString)
    picture = graphene.Field(StandardAttributeString)
    uris = graphene.Field(StandardAttributeValues)
    phone_numbers = graphene.Field(StandardAttributeValues)
    alternative_name = graphene.Field(StandardAttributeString)


class Query(graphene.ObjectType):
    """GraphQL Query class for the V2 Profiles."""

    profiles = graphene.List(CoreProfile)
    profile = graphene.Field(CoreProfile, userId=graphene.String(required=True))

    def resolve_profiles(self, info, **kwargs):
        """GraphQL resolver for the profiles attribute."""
        resp = requests.get('http://localhost:5000/persistent/users').json()
        if not is_json(resp):
            resp = json.dumps(resp)

        return json2obj(resp)

    def resolve_profile(self, info, **kwargs):
        """GraphQL resolver for a single profile."""

        resp = requests.get('http://localhost:5000/persistent/users').json()

        if not is_json(resp):
            resp = json.dumps(resp)

        data = json2obj(resp)
        user_id = kwargs.get('userId')
        for profile in data:
            if profile['user_id']['value'] == user_id:
                return profile
        return None


# Mutations section
class SimpleInputField(graphene.InputObjectType):
    """Simple Input Field that accepts a string argument."""
    value = graphene.String(required=False)


class BasicProfileInput(graphene.InputObjectType):
    """Basic Profile Mutation for the v2 profile schema."""
    first_name = graphene.InputField(SimpleInputField)
    last_name = graphene.InputField(SimpleInputField)
    primary_email = graphene.InputField(SimpleInputField)


class EditBasicProfile(graphene.Mutation):

    class Arguments:
        basic_profile_data = BasicProfileInput(required=False)
        # Get the user_id for editing
        user_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    updated_profile = graphene.Field(lambda: CoreProfile)

    @staticmethod
    def mutate(root, info, user_id, basic_profile_data=None):
        """Update the Basic information of a Profile."""

        db = TinyDB('iam_profile_faker/db.json')
        profile = db.get(tinydb_query().user_id.value == user_id)
        if basic_profile_data:
            for k, v in basic_profile_data.items():
                profile[k].update(v)
            db.update(profile)
            return EditBasicProfile(
                updated_profile=json2obj(json.dumps(profile)))
        return None


class ProfileMutations(graphene.ObjectType):
    """Edit Profiles."""
    edit_basic_profile = EditBasicProfile.Field()
