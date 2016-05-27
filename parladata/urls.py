from django.conf.urls import patterns, include, url
from parladata.views import *

urlpatterns = patterns('',
	url(r'^getActivity/(?P<person_id>\d+)', getActivity),
	url(r'^getMPs', getMPs),
	url(r'^getMPStatic/(?P<person_id>\d+)', getMPStatic),
	url(r'^getSessions/', getSessions),
	url(r'^getNumberOfMPAttendedSessions/(?P<person_id>\d+)', getNumberOfMPAttendedSessions),
    url(r'^getNumberOfAllMPAttendedSessions', getNumberOfAllMPAttendedSessions),
	url(r'^getSpeechesOfMP/(?P<person_id>\d+)', getSpeechesOfMP),
    url(r'^getAllSpeeches', getAllSpeeches),
	url(r'^getVotes/(?P<date>[\w].+)', getVotes),
    url(r'^getVotes/', getVotes),
	url(r'^getSpeeches/(?P<person_id>\d+)',getSpeeches),
	url(r'^getMembersOfPGs/',getMembersOfPGs),
	url(r'^getCoalitionPGs/',getCoalitionPGs),
    url(r'^getMPParty/(?P<person_id>\d+)', getMPParty),
    url(r'^getNumberOfSeatsOfPG/(?P<pg_id>\d+)',getNumberOfSeatsOfPG),
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)',getBasicInfOfPG),
    url(r'^getAllPGs/',getAllPGs),
	url(r'^getAllPGsExt/',getAllPGsExt),
    url(r'^getAllOrganizations/',getAllOrganizations),
    url(r'^getAllPeople/',getAllPeople),
    url(r'^getAllBallots/',getAllBallots),
    url(r'^getAllVotes/',getAllVotes),
    url(r'^motionOfSession/(?P<id_se>\d+)',motionOfSession),
    url(r'^getVotesOfMotion/(?P<motion_id>\d+)',getVotesOfMotion),
    url(r'^getVotesOfSession/(?P<id_se>\d+)',getVotesOfSession),
    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)', getNumberOfPersonsSessions),
    url(r'^getNumberOfFormalSpeeches/(?P<person_id>\d+)', getNumberOfFormalSpeeches),
    url(r'^getExtendedSpeechesOfMP/(?P<person_id>\d+)', getExtendedSpeechesOfMP),
	url(r'^getTaggedVotes/(?P<person_id>\d+)', getTaggedVotes),
    url(r'^getMembersOfPGsOnDate/(?P<date>[\w].+)',getMembersOfPGsOnDate),
    url(r'^getMembersOfPGsRanges/(?P<date>[\w].+)',getMembersOfPGsRanges),
    url(r'^getMembershipsOfMember/(?P<person_id>\d+)/(?P<date>[\w].+|)',getMembershipsOfMember)


)
