# -*- coding: utf-8 -*-

"""Console script for iam_profile_faker."""
import json
import os
import sys

import click

from tinydb import TinyDB

from iam_profile_faker import V2ProfileFactory


@click.group()
def main():
    pass


@click.command()
def create(*args, **kwargs):
    """Create single IAM profile v2 object."""

    factory = V2ProfileFactory()
    output = factory.create(export_json=True)
    click.echo(output)


@click.command()
@click.option('--count', type=int, help='Number of v2 profile objects to create')
def create_batch(count):
    """Create batch IAM profile v2 objects."""

    if count < 1:
        raise click.BadParameter('count needs to be > 0')

    factory = V2ProfileFactory()
    output = factory.create_batch(count, export_json=True)
    click.echo(output)


@click.command()
@click.option('--count', type=int, default=100,
              help='Number of v2 profile objects to create in the db.')
@click.argument('dbname', default='db')
def populate_db(count, dbname):
    """Create batch IAM profile v2 objects and insert them in the database."""

    path = os.path.dirname(os.path.abspath(__file__))

    if not dbname.endswith('.json'):
        dbname = '{0}.json'.format(dbname)

    click.echo('Creating database {0}'.format(dbname))

    db = TinyDB(os.path.join(path, dbname))
    users = V2ProfileFactory().create_batch(count, export_json=False)
    db.insert_multiple(users)

    click.echo('Added {0} profiles in database {1}.'.format(count, dbname))


@click.command()
@click.option('--hris', type=click.Path(exists=True),
              help='Path to file that includes the HRIS data. ')
@click.option('--ldap', type=click.Path(exists=True),
              help='Path to file that includes the LDAP data. ')
def dinopark_data(hris, ldap):
    """Generate data dump to bootstrap dinopark data source"""

    # Profiles storage
    profiles = dict()

    with open(hris, 'r') as data:
        hris_json = json.load(data)
    with open(ldap, 'r') as data:
        ldap_json = json.load(data)

    for hris_obj in hris_json:
        hris_pk = hris_obj['PrimaryWorkEmail']
        for ldap_key, ldap_obj in ldap_json.items():
            ldap_pk = ldap_obj['primary_email']['value']
            if hris_pk == ldap_pk:
                profile = {
                    'hris': hris_obj,
                    'ldap': ldap_obj
                }
                profiles[ldap_pk] = profile


            if ldap_pk not in profiles.keys():
                profile = {
                    'ldap': ldap_obj
                }
                profiles[ldap_pk] = profile

        if hris_pk not in profiles.keys():
            profiles[hris_pk] = {
                'hris': hris_obj
            }

    # Populate profile v2 storage
    v2_storage = []
    for profile in profiles.values():
        if set(profile.keys()) == set(['ldap', 'hris']):
            v2_obj = {
                'businessTitle':  {
                    'value': profile['hris']['businessTitle']
                },
                'team': {
                    'value': profile['hris']['Team']
                },
                'entity': {
                    'value': profile['hris']['Entity']
                },
                'locationDescription': {
                    'value': profile['hris']['LocationDescription']
                },
                'timeZone': {
                    'value': profile['hris']['Time_Zone']
                },
                'workerType': {
                    'value': profile['hris']['WorkerType']
                },
                'workersManager': {
                    'value': profile['hris']['WorkersManagersEmployeeID']
                },
                'wprDeskNumber': {
                    'value': profile['hris']['WPRDeskNumber']
                },
                'costCenter': {
                    'value': profile['hris']['Cost_Center']
                },
                'firstName': {
                    'value': profile['ldap']['first_name']['value']
                },
                'lastName': {
                    'value': profile['ldap']['last_name']['value']
                },
                'funTitle': {
                    'value': profile['ldap']['fun_title']['value']
                },
                'funTitle': {
                    'value': profile['ldap']['fun_title']['value']
                },
                'picture': {
                    'value': profile['ldap']['picture']['value']
                },
                'pronouns': {
                    'value': profile['ldap']['pronouns']['value']
                },
                'alternativeName': {
                    'value': profile['ldap']['alternative_name']['value']
                },
                'locationPreference': {
                    'value': profile['ldap']['location_preference']['value']
                },
                'officeLocation': {
                    'value': profile['ldap']['office_location']['value']
                },
                'description': {
                    'value': profile['ldap']['description']['value']
                },
                'userId': {
                    'value': profile['ldap']['user_id']['value']
                },
                'created': {
                    'value': profile['ldap']['created']['value']
                },
                'lastModified': {
                    'value': profile['ldap']['last_modified']['value']
                },
                'pgpPublicKeys': {
                    'values': profile['ldap']['pgp_public_keys']['values']
                },
                'sshPublicKeys': {
                    'values': profile['ldap']['ssh_public_keys']['values']
                },
                'tags': {
                    'values': profile['ldap']['tags']['values']
                },
                'preferredLanguage': {
                    'values': profile['ldap']['preferred_languages']['values']
                }
            }

            v2_storage.append(v2_obj)

    click.echo(json.dumps(v2_storage))


main.add_command(create)
main.add_command(create_batch)
main.add_command(populate_db)
main.add_command(dinopark_data)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
