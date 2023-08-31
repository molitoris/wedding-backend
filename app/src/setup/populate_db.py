import sys
import pandas as pd
from pathlib import Path

sys.path.append('/workspaces/wedding-api/app')

from src.code_generator import generate_code, hash_string
from src.database.models import User, Guest

from src.database.db import Base, engine, SessionLocal

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    invitation_codes = {}

    p = Path('./data/guests.csv')
    print(p.absolute())
    df = pd.read_csv(p, header=0, delimiter=';')


    session = SessionLocal()


    for group_id in df['group'].unique():
        invitation_token = generate_code(8)
        inviation_hash = hash_string(invitation_token)
        invitation_codes[inviation_hash] = invitation_token
        i = User(invitation_hash=inviation_hash, status=0, email_verification_hash=None, last_login=None, email=None, password_hash=None)

        for id, row in df.loc[df['group'] == group_id, :].iterrows():
            i.associated_guests.append(Guest(first_name=row.first_name, last_name=row.last_name, status=0, food_option=0, allergies=''))

        session.add(i)

    session.commit()
    session.close()

    print(invitation_codes)
