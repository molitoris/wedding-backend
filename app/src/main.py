import csv



with open('./data/guests.csv') as f:
    data = csv.reader(f)

    for row in data:
        print(row)