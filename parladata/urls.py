from django.conf.urls import patterns, url
from parladata.views import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ

from parladata.admin import PersonAutocomplete, PostAutocomplete, MembershipAutocomplete

urlpatterns = patterns('',

    # autocomplete urls
    url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete'),
    url(r'^membership-autocomplete/$', MembershipAutocomplete.as_view(), name='membership-autocomplete'),
    url(r'^post-autocomplete/$', PostAutocomplete.as_view(), name='post-autocomplete'),

    # MPs URLs with and without dates
    url(r'^getActivity/(?P<person_id>\d+)', getActivity),

    url(r'^getMPs/(?P<date_>[\w].+)', getMPs),
    url(r'^getMPs', getMPs),

    url(r'^getMPStatic/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMPStatic),
    url(r'^getMPStatic/(?P<person_id>\d+)', getMPStatic),

    url(r'^getNumberOfMPAttendedSessions/(?P<person_id>\d+)', getNumberOfMPAttendedSessions), # TODO delete
    url(r'^getNumberOfAllMPAttendedSessions/(?P<date_>[\w].+)', getNumberOfAllMPAttendedSessions),

    url(r'^getSpeechesOfMP/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfMP),
    url(r'^getSpeechesOfMP/(?P<person_id>\d+)', getSpeechesOfMP),

    url(r'^getSpeechesOfMPbyDate/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfMPbyDate), # TODO delete

    url(r'^getAllMPsSpeeches/(?P<date_>[\w].+)', getAllSpeechesOfMPs),
    url(r'^getAllMPsSpeeches', getAllSpeechesOfMPs),

    url(r'^getSpeeches/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeeches),
    url(r'^getSpeeches/(?P<person_id>\d+)', getSpeeches),

    url(r'^getMPSpeechesIDs/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesIDs), # TODO check

    url(r'^getAllTimeMPs/(?P<date_>[\w].+)', getAllTimeMPs), # TODO delete
    url(r'^getAllTimeMPs', getAllTimeMPs), # TODO delete

    url(r'^getSpeechesInRange/(?P<person_id>\d+)/(?P<date_from>[\w].+)/(?P<date_to>[\w].+)', getSpeechesInRange),
    url(r'^getMPParty/(?P<person_id>\d+)', getMPParty),
    url(r'^getAllPeople/', getAllPeople),

    url(r'^getExtendedSpeechesOfMP/(?P<person_id>\d+)', getExtendedSpeechesOfMP), # TODO check

    url(r'^getPersonData/(?P<person_id>\d+)', getPersonData), # TODO check

    url(r'^getMembershipsOfMember/(?P<person_id>\d+)/(?P<date>[\w].+|)', getMembershipsOfMember),

    url(r'^getMembersWithFuction/', getMembersWithFuction), # TODO fix spelling

    url(r'^getNumberOfFormalSpeeches/(?P<person_id>\d+)', getNumberOfFormalSpeeches), # TODO check and decide if delete
    url(r'^getTaggedVotes/(?P<person_id>\d+)', getTaggedVotes), # TODO delete

    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)/(?P<date_>[\w].+)', getNumberOfPersonsSessions),
    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)', getNumberOfPersonsSessions),

    url(r'^getAllQuestions/(?P<date_>[\w].+)', getAllQuestions),
    url(r'^getAllQuestions/', getAllQuestions),
    url(r'^getAllChangesAfter/(?P<person_update_time>[\w].+)/(?P<session_update_time>[\w].+)/(?P<speech_update_time>[\w].+)/(?P<ballots_update_time>[\w].+)/(?P<question_update_time>[\w].+)', getAllChangesAfter),

    url(r'^getDistricts', getDistricts),
    url(r'^getAllTimeMemberships', getAllTimeMemberships),

    # PGs URLs with and without dates
    url(r'^getMembersOfPGs/', getMembersOfPGs),
    url(r'^getCoalitionPGs/', getCoalitionPGs),
    url(r'^getNumberOfSeatsOfPG/(?P<pg_id>\d+)', getNumberOfSeatsOfPG),

    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)/(?P<date_>[\w].+)', getBasicInfOfPG),
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),

    url(r'^getAllPGs/(?P<date_>[\w].+)', getAllPGs),
    url(r'^getAllPGs/', getAllPGs),

    url(r'^getAllPGsExt/', getAllPGsExt),
    url(r'^getAllOrganizations/', getAllOrganizations),

    url(r'^getMembersOfPGsOnDate/(?P<date_>[\w].+)', getMembersOfPGsOnDate),
    url(r'^getMembersOfPGsOnDate', getMembersOfPGsOnDate),

    url(r'^getMembersOfPGsRanges/(?P<date_>[\w].+)', getMembersOfPGsRanges),
    url(r'^getMembersOfPGsRanges', getMembersOfPGsRanges),

    url(r'^getMembersOfPGRanges/(?P<org_id>\d+)/(?P<date_>[\w].+)', getMembersOfPGRanges),
    url(r'^getMembersOfPGRanges/(?P<org_id>\d+)', getMembersOfPGRanges),

    url(r'^getOrganizatonByClassification', getOrganizatonByClassification),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)/(?P<date_>[\w].+)', getOrganizationRolesAndMembers),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)', getOrganizationRolesAndMembers),

    url(r'^getPGsSpeechesIDs/(?P<org_id>\d+)/(?P<date_>[\w].+)', getPGsSpeechesIDs),

    # Votes and Motion URLs
    url(r'^getAllVotes/(?P<date_>[\w].+)', getAllVotes), # TODO refactor with getVotes
    url(r'^getAllVotes/', getAllVotes),
    url(r'^getDocumentOfMotion/(?P<motion_id>[\w].+)', getDocumentOfMotion), # TODO delete
    url(r'^isVoteOnDay/(?P<date_>[\w].+)', isVoteOnDay),
    url(r'^isVoteOnDay/', isVoteOnDay),
    url(r'^getTags', getTags),
    url(r'^getVotes/(?P<date_>[\w].+)', getVotes), # TODO refactor with getAllVotes
    url(r'^getVotes/', getVotes), # TODO refactor with getAllVotes
    url(r'^motionOfSession/(?P<id_se>\d+)', motionOfSession),
    url(r'^getVotesOfMotion/(?P<motion_id>\d+)', getVotesOfMotion),
    url(r'^getVotesOfSession/(?P<id_se>\d+)', getVotesOfSession),

    # Ballots URLs
    url(r'^getAllBallots/(?P<date_>[\w].+)', getAllBallots),
    url(r'^getAllBallots/', getAllBallots),
    
    url(r'^getBallotsCounterOfPerson/(?P<person_id>\d+)/(?P<date_>[\w].+|)', getBallotsCounterOfPerson),
    url(r'^getBallotsCounterOfPerson/(?P<person_id>\d+)', getBallotsCounterOfPerson),

    url(r'^getBallotsCounterOfParty/(?P<party_id>\d+)/(?P<date_>[\w].+|)', getBallotsCounterOfParty),
    url(r'^getBallotsCounterOfParty/(?P<party_id>\d+)', getBallotsCounterOfParty),

    url(r'^getVotesTable/(?P<date_to>[\w].+|)', getVotesTable),
    url(r'^getVotesTable/', getVotesTable),

    # Sessions URLs
    url(r'^getSessions/(?P<date_>[\w].+)', getSessions),
    url(r'^getSessions/', getSessions),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)/(?P<date_>[\w].+)', getSessionsOfOrg),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)', getSessionsOfOrg),

    # Speech URLs
    url(r'^getAllSpeeches/(?P<date_>[\w].+)', getAllSpeeches), # TODO refactor with other speeches
    url(r'^getAllSpeeches', getAllSpeeches), # TODO refactor with other speeches
    url(r'^isSpeechOnDay/(?P<date_>[\w].+)', isSpeechOnDay),
    url(r'^isSpeechOnDay/', isSpeechOnDay),
    url(r'^getSpeechData/(?P<speech_id>\d+)', getSpeechData),
    url(r'^getAllAllSpeeches/$', getAllAllSpeeches),

    # POST save url's for parser
    url(r'^addQuestion/', addQuestion),

    # debug helpers
    url(r'^getMembershipDuplications', getMembershipDuplications),
    url(r'^postMembersFixer', postMembersFixer),
    url(r'^membersFlowInOrg', membersFlowInOrg),
    url(r'^membersFlowInPGs', membersFlowInPGs),
    url(r'^membersFlowInDZ', membersFlowInDZ),
    url(r'^checkSessions/(?P<date_>[\w].+)', checkSessions),

    # MONITORING
    url(r'^monitoring', monitorMe),
)
