from django.conf.urls import patterns, include, url
from parladata.views import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ

from parladata.admin import PersonAutocomplete, PostAutocomplete, MembershipAutocomplete

urlpatterns = patterns('',

    #autocomplete urls
    url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete'),
    url(r'^membership-autocomplete/$', MembershipAutocomplete.as_view(), name='membership-autocomplete'),
    url(r'^post-autocomplete/$', PostAutocomplete.as_view(), name='post-autocomplete'),

    url(r'^getActivity/(?P<person_id>\d+)', getActivity),
    url(r'^getMPs/(?P<date_>[\w].+)', getMPs),
    url(r'^getMPs', getMPs),

    url(r'^getMPStatic/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMPStatic),
    url(r'^getMPStatic/(?P<person_id>\d+)', getMPStatic),
    url(r'^getSessions/(?P<date_>[\w].+)', getSessions),
    url(r'^getSessions/', getSessions),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)/(?P<date_>[\w].+)', getSessionsOfOrg),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)', getSessionsOfOrg),
    url(r'^getNumberOfMPAttendedSessions/(?P<person_id>\d+)', getNumberOfMPAttendedSessions),
    url(r'^getNumberOfAllMPAttendedSessions/(?P<date_>[\w].+)', getNumberOfAllMPAttendedSessions),
    url(r'^getSpeechesOfMP/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfMP),
    url(r'^getSpeechesOfMP/(?P<person_id>\d+)', getSpeechesOfMP),
    url(r'^getSpeechesOfMPbyDate/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfMPbyDate),
    url(r'^getAllSpeeches/(?P<date_>[\w].+)', getAllSpeeches),
    url(r'^getAllSpeeches', getAllSpeeches),
    url(r'^getAllMPsSpeeches/(?P<date_>[\w].+)', getAllSpeechesOfMPs),
    url(r'^getAllMPsSpeeches', getAllSpeechesOfMPs),

    url(r'^getVotes/(?P<date_>[\w].+)', getVotes),
    url(r'^getVotes/', getVotes),

    url(r'^getSpeeches/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeeches),
    url(r'^getSpeeches/(?P<person_id>\d+)', getSpeeches),

    url(r'^getMPSpeechesIDs/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesIDs),
    url(r'^getPGsSpeechesIDs/(?P<org_id>\d+)/(?P<date_>[\w].+)', getPGsSpeechesIDs),

    url(r'^getSpeechesInRange/(?P<person_id>\d+)/(?P<date_from>[\w].+)/(?P<date_to>[\w].+)', getSpeechesInRange),

    url(r'^getMembersOfPGs/',getMembersOfPGs),
    url(r'^getCoalitionPGs/',getCoalitionPGs),
    url(r'^getMPParty/(?P<person_id>\d+)', getMPParty),
    url(r'^getNumberOfSeatsOfPG/(?P<pg_id>\d+)',getNumberOfSeatsOfPG),

    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)',getBasicInfOfPG),
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)',getBasicInfOfPG),
    url(r'^getAllPGs/(?P<date_>[\w].+)',getAllPGs),
    url(r'^getAllPGs/',getAllPGs),
    url(r'^getAllPGsExt/',getAllPGsExt),
    url(r'^getAllOrganizations/',getAllOrganizations),
    url(r'^getAllPeople/',getAllPeople),

    url(r'^getAllBallots/(?P<date_>[\w].+)',getAllBallots),
    url(r'^getAllBallots/',getAllBallots),

    url(r'^getAllVotes/(?P<date_>[\w].+)',getAllVotes),
    url(r'^getAllVotes/',getAllVotes),

    url(r'^motionOfSession/(?P<id_se>\d+)',motionOfSession),
    url(r'^getVotesOfMotion/(?P<motion_id>\d+)',getVotesOfMotion),
    url(r'^getVotesOfSession/(?P<id_se>\d+)',getVotesOfSession),

    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)/(?P<date_>[\w].+)', getNumberOfPersonsSessions),
    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)', getNumberOfPersonsSessions),

    url(r'^getNumberOfFormalSpeeches/(?P<person_id>\d+)', getNumberOfFormalSpeeches),
    url(r'^getExtendedSpeechesOfMP/(?P<person_id>\d+)', getExtendedSpeechesOfMP),
    url(r'^getTaggedVotes/(?P<person_id>\d+)', getTaggedVotes),

    url(r'^getMembersOfPGsOnDate/(?P<date_>[\w].+)',getMembersOfPGsOnDate),
    url(r'^getMembersOfPGsOnDate',getMembersOfPGsOnDate),

    url(r'^getMembersOfPGsRanges/(?P<date_>[\w].+)',getMembersOfPGsRanges),
    url(r'^getMembersOfPGsRanges',getMembersOfPGsRanges),
    url(r'^getMembersOfPGRanges/(?P<org_id>\d+)/(?P<date_>[\w].+)',getMembersOfPGRanges),
    url(r'^getMembersOfPGRanges/(?P<org_id>\d+)',getMembersOfPGRanges),

    url(r'^getMembersOfOrgsRanges/(?P<org_id>\d+)/(?P<date_>[\w].+)',getMembersOfOrgsRanges),
    url(r'^getMembersOfOrgsRanges/(?P<org_id>\d+)',getMembersOfOrgsRanges),

    url(r'^getMembershipsOfMember/(?P<person_id>\d+)/(?P<date>[\w].+|)',getMembershipsOfMember),
    url(r'^getAllTimeMemberships',getAllTimeMemberships),
    url(r'^getAllTimeMPs/(?P<date_>[\w].+)',getAllTimeMPs),
    url(r'^getAllTimeMPs',getAllTimeMPs),
    url(r'^getOrganizatonByClassification',getOrganizatonByClassification),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)/(?P<date_>[\w].+)',getOrganizationRolesAndMembers),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)',getOrganizationRolesAndMembers),

    url(r'^getTags', getTags),

    url(r'^getDistricts', getDistricts),

    url(r'^getSpeechData/(?P<speech_id>\d+)',getSpeechData),
    url(r'^getResultOfMotion/(?P<motion_id>\d+)',getResultOfMotion),

    url(r'^getPersonData/(?P<person_id>\d+)',getPersonData),

    url(r'^isSpeechOnDay/(?P<date_>[\w].+)', isSpeechOnDay),
    url(r'^isSpeechOnDay/', isSpeechOnDay),

    url(r'^isVoteOnDay/(?P<date_>[\w].+)', isVoteOnDay),
    url(r'^isVoteOnDay/', isVoteOnDay),

    url(r'^getMembersWithFuction/', getMembersWithFuction),

    url(r'^getDocumentOfMotion/(?P<motion_id>[\w].+)', getDocumentOfMotion),


    #debug helpers
    url(r'^getMembershipDuplications', getMembershipDuplications),
    url(r'^parserChecker', parserChecker), 
    url(r'^postMembersFixer', postMembersFixer),
    url(r'^membersFlowInOrg', membersFlowInOrg),
    url(r'^membersFlowInPGs', membersFlowInPGs),
    url(r'^membersFlowInDZ', membersFlowInDZ),

    url(r'^sejee/(?P<date_>[\w].+)',checkSessions),
)
