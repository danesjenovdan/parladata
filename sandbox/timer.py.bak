# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime, timedelta
import time
import requests

gen_url = ['getMPs', 'getIDsOfAllMinisters', 'getAllPeople', 'getPersonData', 'getMembersWithFunction',
		   'getAllQuestions', 'getDistricts', 'getAllTimeMemberships', 'getMembersOfPGs', 'getCoalitionPGs',
		   'getAllPGs', 'getAllPGsExt', 'getAllOrganizations', 'getMembersOfPGsOnDate', 'getMembersOfPGsRanges',
		   'getOrganizatonsByClassification', 'getVotes', 'isVoteOnDay', 'getTags', 'getAllBallots', 'getVotesTable',
		   'getVotesTableExtended', 'getSessions', 'getAllSpeeches', 'isSpeechOnDay', 'getAllAllSpeeches', 'getAllMPsSpeeches']

person_url = ['getMPStatic', 'getMinistrStatic', 'getMPParty', 'getMembershipsOfMember', 'getNumberOfPersonsSessions',
			  'getBallotsCounterOfPerson', 'getSpeechesOfMP', 'getSpeeches', 'getMPSpeechesIDs', 'getSpeechesInRange']

pg_url = ['getNumberOfSeatsOfPG', 'getBasicInfOfPG', 'getMembersOfPGRanges', 'getOrganizationRolesAndMembers',
		  'getPGsSpeechesIDs', 'getBallotsCounterOfParty']

s_url = ['motionOfSession', 'getBallotsOfSession', 'getVotesOfSessionTable']

v_url = ['getBallotsOfMotion']
wb_url = ['getSessionsOfOrg']
sp_url = ['getSpeechData']

urls = [{'type': 'gen', 'urls': gen_url, 'id': ''},
		{'type': 'person', 'urls': person_url, 'id': 11},
		{'type': 'pg', 'urls': pg_url, 'id': 5},
		{'type': 's', 'urls': s_url, 'id': 5583},
		{'type': 'v', 'urls': v_url, 'id': 5125},
		{'type': 'wb', 'urls': wb_url, 'id': 28},
		{'type': 'sp', 'urls': sp_url, 'id': 590896}]

def tajmer(base_url, endpoints, id_):
    data = []
    for endpoint in endpoints:
        start = time.time()
        print base_url + endpoint + '/' + str(id_)
        resp = requests.get(base_url + endpoint + '/' + str(id_))
        end = time.time()
        data.append({'endpoint': endpoint,
                     'time': (end - start),
                     'status': resp.status_code})
    return data


def measureApiTimes(urls):
	base_url = 'https://data.parlameter.si/v1/'
	data = {}
	for url in urls:
		data[url['type']] = tajmer(base_url, url['urls'], url['id'])
	return data