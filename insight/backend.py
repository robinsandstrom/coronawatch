import csv

def load_csv():
    data = []
    with open('insight/total.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            data_row = []
            for cell in row:
                data_row.append(float(cell))
            data.append(data_row)
    return data
