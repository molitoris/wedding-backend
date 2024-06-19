import random
import csv
from typing import Dict
from faker import Faker

def generate_random_guest(fake: Faker, group_id: int, role: str) -> Dict:
    return {
        'group': group_id,
        'last_name': fake.last_name(),
        'first_name': fake.first_name(),
        'roles': role
    }


def generate_random_guest_list(fake: Faker, nguests: int = 12, nadmin: int = 1, nwitness: int = 2):

    # Data to be generated
    data = []
    group_number = 0

    for _ in range(nadmin):
        data.append(generate_random_guest(fake=fake, group_id=group_number, role='admin'))
        group_number += 1
    
    for _ in range(nwitness):
        data.append(generate_random_guest(fake=fake, group_id=group_number, role='witness'))
        group_number += 1

    for _ in range(nguests):
        data.append(generate_random_guest(fake=fake, group_id=group_number, role='guest'))

        if not random.choices([True, False], weights=[0.2, 0.8], k=1)[0]:
            group_number += 1
    
    return data


if __name__ == '__main__':


    # Initialize Faker
    fake = Faker()

    Faker.seed(42)
    random.seed(42)

    data = generate_random_guest_list(fake=fake)

    # File path
    file_path = 'data/raw/guest_list.csv'

    # Writing to csv file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=['group', 'last_name', 'first_name', 'roles'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)