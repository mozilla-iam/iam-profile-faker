# -*- coding: utf-8 -*-

"""Console script for iam_profile_faker."""
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


main.add_command(create)
main.add_command(create_batch)
main.add_command(populate_db)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
