import os
import pandas as pd
import json
import pathlib
import logging
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.security import generate_token, hash_token
from src.database.db_tables import User, Guest, Role
from src.database.models.user_status import UserStatus
from src.database.models.food_options import FoodOption
from src.database.models.dessert_options import DessertOption
from src.database.models.guest_status import GuestStatus
from src.database.models.guest_role import GuestRole
from src.setup.qr_code import QrCodeImageGenerator
from src.database.db_base import Base

from src.config.app_config import load_config

def _get_role(row) -> List[Role]:
    roles = []
    for role in row.roles.split(', '):
        role = role.lower().strip()
        if role == 'guest':
            roles.append(Role(name=GuestRole.GUEST))
        elif role == 'witness':
            roles.append(Role(name=GuestRole.WITNESS))
        elif role == 'admin':
            roles.append(Role(name=GuestRole.ADMIN))
        else:
            raise AttributeError(f'Unknown role {role}')
    return roles


def populate_db():
    config = load_config()

    sql_file = pathlib.Path(config.db.get_file_path())

    sql_file.parent.mkdir(parents=True, exist_ok=True)

    # Create table
    engine = create_engine(f"sqlite:///{sql_file}", echo=True,
                           connect_args={"check_same_thread": False})

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(engine)

    guest_list_file_path = config.setup.guest_list_filepath

    logging.info(f'Loading guest list from {guest_list_file_path}')

    df = pd.read_csv(guest_list_file_path, header=0, delimiter=';')

    guest_registration_url = config.frontend_base_url + config.setup.guest_registration_endpoint

    # QR Code
    qr_generator = QrCodeImageGenerator()
    qr_code_path = config.setup.get_qr_code_output_path()
    qr_code_path.mkdir(parents=True, exist_ok=True)

    # Inviation data
    invitation_path = config.setup.invitation_data_output_path
    invitation_filepath = config.setup.get_invitation_file_path()
    invitation_path.mkdir(parents=True, exist_ok=True)

    invitation_codes = {}

    session = SessionLocal()

    for group_id in df['group'].unique():
        # Generate token
        invitation_token = generate_token(config.setup.invitation_token_size)
        inviation_hash = hash_token(invitation_token)

        # Create user
        user = User(invitation_hash=inviation_hash, status=UserStatus.UNSEEN,
                    email_verification_hash=None, last_login=None, email=None,
                    password_hash=None)

        names = []
        # Store token with guest names
        invitation_codes[inviation_hash] = {'token': invitation_token, 'guests': []}

        # Associate guest based on group id
        for _, row in df.loc[df['group'] == group_id, :].iterrows():
            roles = _get_role(row)
            user.associated_guests.append(Guest(first_name=row.first_name,
                                                last_name=row.last_name,
                                                status=GuestStatus.UNDEFINED,
                                                food_option=FoodOption.UNDEFINED,
                                                dessert_option=DessertOption.UNDEFINED,
                                                allergies='',
                                                favorite_fairy_tale_character='',
                                                favorite_tool='',
                                                roles=roles))


            invitation_codes[inviation_hash]['guests'].append({'first_name': row.first_name,
                                                               'last_name': row.last_name,
                                                               'role': row. roles})

            names.append(f'{row.last_name}_{row.first_name}')

        # Generate QR Code for user registration
        file_name = '_'.join(names)
        qr_generator.get_image(text=guest_registration_url + invitation_token,
                               output_path=qr_code_path.joinpath(file_name).with_suffix('.png'))

        session.add(user)

    session.commit()
    session.close()

    with open(invitation_filepath, 'w') as f:
        f.write(json.dumps(invitation_codes, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    os.environ['APP_ENV'] = 'production'
    # os.environ['APP_ENV'] = 'dev'
    populate_db()
