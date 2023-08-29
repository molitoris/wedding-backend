import csv
import pandas as pd
from pathlib import Path

from app.src.code_generator import generate_code, hash_string
from app.src.model import Invitation, Guest

invitations = {}

invitation_codes = {}

p = Path('../../data/guests.csv')
df = pd.read_csv(p, header=0, delimiter=';')

for group_id in df['group'].unique():
    invitation_code = generate_code(8)
    hashed_code = hash_string(invitation_code)
    invitation_codes[hashed_code] = invitation_code
    invitations[group_id] = Invitation(id=group_id, invitation_code=hashed_code)

for id, row in df.iterrows():
    invitations[row.group].associated_guests.append(Guest(first_name=row.first_name, last_name=row.last_name))

pass