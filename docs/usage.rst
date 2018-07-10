=====
Usage
=====

To use iam-profile-faker in a project::

    from iam_profile_faker.factory import V2ProfileFactory


    factory = V2ProfileFactory()
    # Generate a single object
    factory.create()

    # Generate a batch of 10 objects
    factory.create_batch(10)

    # Generate a single object serialized to JSON
    factory.create(export_json=True)

    # Generate a batch of 10 objects serialized to JSON
    factory.create_batch(10, export_json=True)


To use iam-profile-faker as a CLI tool::

    $ iam_profile_faker --help
    Usage: iam_profile_faker [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
    create        Create single IAM profile v2 object.
    create_batch  Create batch IAM profile v2 objects.
