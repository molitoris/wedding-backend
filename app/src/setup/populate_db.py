import sys
import pandas as pd
from pathlib import Path
import json

sys.path.append('/workspaces/wedding-api/app')

from src.security import generate_token, hash_token
from src.database.db_tables import User, Guest, Role
from src.database.models.user_status import UserStatus
from src.database.models.user_role import UserRole
from src.setup.qr_code import QrCodeImageGenerator

from src.database.db import Base, engine, SessionLocal
from src.config.app_config import load_config

if __name__ == '__main__':

    config = load_config()

    # Create table
    Base.metadata.create_all(engine)

    print(config.setup.guest_list_filepath.absolute())
    df = pd.read_csv(config.setup.guest_list_filepath, header=0, delimiter=';')

    guest_registration_url = config.frontend_base_url + config.setup.guest_registration_endpoint

    # QR Code
    qr_generator = QrCodeImageGenerator()
    qr_code_path = config.setup.qr_code_output_path
    qr_code_path.mkdir(parents=True, exist_ok=True)

    # Inviation data
    invitation_path = config.setup.invitation_data_output_path
    invitation_filepath = invitation_path.joinpath(config.setup.invitation_data_filename)
    invitation_path.mkdir(parents=True, exist_ok=True)

    invitation_codes = {}

    session = SessionLocal()

    for group_id in df['group'].unique():
        # Generate token
        invitation_token = generate_token(config.setup.invitation_token_size)
        inviation_hash = hash_token(invitation_token)
        
        # Create user
        user = User(invitation_hash=inviation_hash, status=UserStatus.UNSEEN, email_verification_hash=None, last_login=None, email=None, password_hash=None)

        names = []

        # Associate guest based on group id
        for id, row in df.loc[df['group'] == group_id, :].iterrows():
            user.associated_guests.append(Guest(first_name=row.first_name, last_name=row.last_name, status=0, food_option=0, allergies=''))

            for role in row.roles.split(', '):
                role = role.lower().strip()
                if role == 'guest':
                    user.role.append(UserRole.GUEST)
                elif role == 'witness':
                    user.role.append(UserRole.WITNESS)
                elif role == 'admin':
                    user.role.append(UserRole.ADMIN)
                else:
                    raise AttributeError('Unknown role')

            names.append(row.first_name)

        # Generate QR Code for user registration
        qr_generator.get_image(text=guest_registration_url + invitation_token, output_path=qr_code_path.joinpath('_'.join(names)).with_suffix('.png'))

        # Store token with guest names
        invitation_codes[inviation_hash] = (invitation_token, ", ".join(names))

        session.add(user)

    session.commit()
    session.close()

    with open(invitation_filepath, 'w') as f:
        f.write(json.dumps(invitation_codes, indent=2, ensure_ascii=False))
