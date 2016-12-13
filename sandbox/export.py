# -*- coding: utf-8 -*-
import csv
import sys

reload(sys)
sys.setdefaultencoding("UTF-8")


def dictToCSV(data, file_name):
    with open('exports/' + file_name, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)

        for key, value in data.items():
            if type(value) == list:
                e_data = value
            else:
                e_data = [value]

            csvwriter.writerow([key] + e_data)
    return 'saved in exports/' + file_name


def listToCSV(data, file_name):
    with open('exports/' + file_name, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile,
                               delimiter=',',
                               quotechar='|',
                               quoting=csv.QUOTE_MINIMAL)

        for value in data:
            if type(value) == list:
                e_data = value
            elif type(value) == tuple:
                e_data = list(value)
            else:
                e_data = [value]
            csvwriter.writerow(e_data)
    return 'saved in exports/' + file_name
