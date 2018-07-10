#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `iam_profile_faker` package."""


import mock
import unittest
from click.testing import CliRunner

from iam_profile_faker import cli
from iam_profile_faker.factory import V2ProfileFactory


class TestIAMProfileFaker(unittest.TestCase):
    """Tests for `iam_profile_faker` package."""

    @mock.patch('iam_profile_faker.factory.IAMFaker.create')
    def test_000_factory_create(self, mock_create):
        """Test create factory."""
        mock_create.return_value = {'foo': 'bar'}
        factory = V2ProfileFactory()
        assert factory.create() == {'foo': 'bar'}

    @mock.patch('iam_profile_faker.factory.IAMFaker.create')
    def test_001_factory_create_batch(self, mock_create):
        """Test create batch factory."""
        mock_create.return_value = {'foo': 'bar'}
        factory = V2ProfileFactory()
        output = [{'foo': 'bar'}, {'foo': 'bar'}]
        assert factory.create_batch(2) == output

    @mock.patch('iam_profile_faker.factory.IAMFaker.create')
    def test_002_command_line_interface_create(self, mock_create):
        """Test create cli."""
        runner = CliRunner()
        mock_create.return_value = {'foo': 'bar'}
        create_result = runner.invoke(cli.main, ['create'])
        assert create_result.exit_code == 0
        assert create_result.output == '{"foo": "bar"}\n'

    @mock.patch('iam_profile_faker.factory.IAMFaker.create')
    def test_003_command_line_interface_create(self, mock_create):
        """Test create cli."""
        runner = CliRunner()
        mock_create.return_value = {'foo': 'bar'}
        create_result = runner.invoke(cli.main, ['create_batch', '--count', 2])
        assert create_result.exit_code == 0
        assert create_result.output == '[{"foo": "bar"}, {"foo": "bar"}]\n'
