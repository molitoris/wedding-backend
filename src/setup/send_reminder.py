import csv
from pathlib import Path
import argparse

from src.email_sender import send_reminer_email


def read_csv_and_create_dict(file_path):
    # Initialize an empty dictionary to store the email-based records
    email_dict = {}

    # Read the CSV file
    with file_path.open('r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row['email']
            details = (row['gender'], row['firstname'])
            if email in email_dict:
                email_dict[email].append(details)
            else:
                email_dict[email] = [details]

    # Sort the lists by gender, with female first
    for email in email_dict:
        email_dict[email].sort(key=lambda x: x[0])

    return email_dict


def main():
    parser = argparse.ArgumentParser(description='Send reminder email.')
    parser.add_argument('file_path', type=str,
                        help='The path to the CSV file [gender, firstname, lastname, email]')
    args = parser.parse_args()

    file_path = Path(args.file_path)

    if not file_path.exists():
        raise AttributeError(f'File not found: {file_path}')

    email_dict = read_csv_and_create_dict(file_path)

    for email, guests in email_dict.items():
        send_reminer_email(guests=guests, receiver_email=email)


if __name__ == '__main__':
    main()
