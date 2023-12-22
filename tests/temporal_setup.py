import os
import pathlib
import json
import tempfile
from unittest.mock import patch
from contextlib import contextmanager

import pytest
import pandas as pd

from src.setup.populate_db import populate_db
from src.config.app_config import load_config


def get_guest_list(*args, **kwargs):
    column_names = ['group', 'last_name', 'first_name', 'roles']

    data = [
        ('0', 'Johnson', 'Emily', 'admin'),

        ('1', 'Doe', 'Jane', 'witness'),

        ('2', 'Doe', 'John', 'witness'),

        ('3', 'Thompson', 'Olivia', 'guest'),

        ('4', 'Rodriguez', 'Ava ', 'guest'),
        ('4', 'Perez', 'Juan', 'guest'),
        ]
    return pd.DataFrame(data=data, columns=column_names)


def load_inivation_data(path: pathlib.Path):
    with open(path, 'r') as f:
        return json.load(f)


@contextmanager
def guest_list_patch():
    with patch('pandas.read_csv', get_guest_list):
        yield


@contextmanager
def temp_file():
    with tempfile.NamedTemporaryFile() as sql_file:
        yield sql_file


@contextmanager
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield pathlib.Path(temp_dir)


@contextmanager
def sql_file_path_patch(temp_file):
    with patch('src.config.app_config.DatabaseSettings.get_file_path', lambda x: temp_file.name):
        yield


@contextmanager
def qr_code_patch(temp_dir):
    with patch('src.config.app_config.Setup.get_qr_code_output_path', lambda x: temp_dir):
        yield


@contextmanager
def invitation_path_patch(temp_file):
    with patch('src.config.app_config.Setup.get_invitation_file_path', lambda x: temp_file.name):
        yield


@pytest.fixture
def setup_db():
    os.environ['APP_ENV'] = 'testing'

    with guest_list_patch(), temp_file() as sql_file, temp_file() as invitation_file, \
        temp_directory() as temp_dir , qr_code_patch(temp_dir), \
        sql_file_path_patch(sql_file), invitation_path_patch(invitation_file):
        populate_db()

        yield


@pytest.fixture
def setup_backend(setup_db):
    config = load_config()
    return load_inivation_data(config.setup.get_invitation_file_path())
