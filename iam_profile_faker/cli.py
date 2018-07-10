# -*- coding: utf-8 -*-

"""Console script for iam_profile_faker."""
import sys
import click

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


main.add_command(create)
main.add_command(create_batch)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
