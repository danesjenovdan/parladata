# -*- coding: utf-8 -*-
import csv
import sys

reload(sys)
sys.setdefaultencoding("UTF-8")

PS = ['poslanska skupina']

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


def getAmendment():
    data = [['PG', 'status', 'link']]
    parliamentaryGroups = Organization.objects.filter(classification__in=PS)
    acronyms = list(set(list(parliamentaryGroups.values_list('acronym', flat=True))))
    amandmas = Vote.objects.filter(name__icontains='amandma')
    for acronym in acronyms:
        temp_amandmas = amandmas.filter(name__icontains="["+acronym).values_list("session_id", "id", "motion__result")
        pg_amandmas = [list(map(str, i))
                       for i
                       in temp_amandmas]
        for amandma in pg_amandmas:
            data.append([acronym, amandma[2], 'https://parlameter.si/seja/glasovanje/' + '/'.join(amandma[:2])])
    listToCSV(data, 'amandmaji.csv')
