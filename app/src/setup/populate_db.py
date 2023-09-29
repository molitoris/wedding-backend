import sys
import pandas as pd
from pathlib import Path
import json

sys.path.append('/workspaces/wedding-api/app')

from src.security import generate_token, hash_token
from src.database.models import User, Guest
from src.setup.qr_code import QrCodeImageGenerator

from src.database.db import Base, engine, SessionLocal

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    invitation_codes = {}

    p = Path('./raw/guests.csv')
    print(p.absolute())
    df = pd.read_csv(p, header=0, delimiter=';')

    base_url = 'https://homepage-beta.molitoris.org/registration?code='
    output_base_path = Path(__file__).parent.joinpath('../../../data/qr_codes')
    output_base_path.mkdir(parents=True)

    session = SessionLocal()

    qr_generator = QrCodeImageGenerator()


    for group_id in df['group'].unique():
        invitation_token = generate_token(8)
        inviation_hash = hash_token(invitation_token)
        i = User(invitation_hash=inviation_hash, status=0, email_verification_hash=None, last_login=None, email=None, password_hash=None)

        names = []
        for id, row in df.loc[df['group'] == group_id, :].iterrows():
            i.associated_guests.append(Guest(first_name=row.first_name, last_name=row.last_name, status=0, food_option=0, allergies=''))
            names.append(row.first_name)

        qr_generator.get_image(text=base_url + invitation_token, output_path=output_base_path.joinpath('_'.join(names)).with_suffix('.png'))

        invitation_codes[inviation_hash] = (invitation_token, ", ".join(names))

        session.add(i)

    session.commit()
    session.close()

    with open(output_base_path.joinpath('../hash_lookup.txt'), 'w') as f:
        f.write(json.dumps(invitation_codes, indent=2, ensure_ascii=False))
