import sys
import pandas as pd
from pathlib import Path

sys.path.append('/workspaces/wedding-api/app')

from src.security import generate_token, hash_token
from src.database.models import User, Guest

from src.database.db import Base, engine, SessionLocal

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    invitation_codes = {}

    p = Path('./raw/guests.csv')
    print(p.absolute())
    df = pd.read_csv(p, header=0, delimiter=';')


    session = SessionLocal()


    for group_id in df['group'].unique():
        invitation_token = generate_token(8)
        inviation_hash = hash_token(invitation_token)
        i = User(invitation_hash=inviation_hash, status=0, email_verification_hash=None, last_login=None, email=None, password_hash=None)

        names = []
        for id, row in df.loc[df['group'] == group_id, :].iterrows():
            i.associated_guests.append(Guest(first_name=row.first_name, last_name=row.last_name, status=0, food_option=0, allergies=''))
            names.append(row.first_name)

        invitation_codes[inviation_hash] = (invitation_token, ", ".join(names))

        session.add(i)

    session.commit()
    session.close()

    print(invitation_codes)
