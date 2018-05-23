from django.conf.urls import url, include
from parladata.views import *
from parladata.api import *
from .utils import getMembershipDuplications, membersFlowInOrg, postMembersFixer, membersFlowInPGs, membersFlowInDZ, checkSessions
from rest_framework import routers
from parladata.admin import PersonAutocomplete, PostAutocomplete, MembershipAutocomplete
from parladata.api import *
from rest_framework import routers

from rest_framework.documentation import include_docs_urls
router = routers.DefaultRouter()
router.register(r'persons', PersonView)
router.register(r'sessions', SessionView)
router.register(r'last_session', LastSessionWithVoteView)
router.register(r'motions', MotionView)
router.register(r'links', LinkView)
router.register(r'ballots', BallotView)
router.register(r'votes', VoteView)
router.register(r'unedited_motions', MotionFilter)
router.register(r'speechs', SpeechView)
router.register(r'organizations', OrganizationView)
router.register(r'law', LawView)
router.register(r'allActiveEpas', AllUniqueEpas)
router.register(r'tags', TagsView)
router.register(r'memberships', MembershipView)
router.register(r'areas', AreaView)
router.register(r'agenda-items', AgendaItemView)

urlpatterns = [    
    # autocomplete urls
    url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete'),
    url(r'^membership-autocomplete/$', MembershipAutocomplete.as_view(), name='membership-autocomplete'),
    url(r'^post-autocomplete/$', PostAutocomplete.as_view(), name='post-autocomplete'),

    # MPs URLs with and without dates
    url(r'^getMPs/(?P<date_>[\w].+)', getMPs),
    url(r'^getMPs', getMPs),

    url(r'^getIDsOfAllMinisters/(?P<date_>[\w].+)', getIDsOfAllMinisters),
    url(r'^getIDsOfAllMinisters', getIDsOfAllMinisters),

    url(r'^getMPStatic/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMPStatic),
    url(r'^getMPStatic/(?P<person_id>\d+)', getMPStatic),

    url(r'^getMinistrStatic/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMinistrStatic),
    url(r'^getMinistrStatic/(?P<person_id>\d+)', getMinistrStatic),

    url(r'^getMPParty/(?P<person_id>\d+)', getMPParty),
    url(r'^getAllPeople/', getAllPeople),

    url(r'^getPersonData/(?P<person_id>\d+)', getPersonData),

    url(r'^getMembershipsOfMember/(?P<person_id>\d+)/(?P<date>[\w].+|)', getMembershipsOfMember),

    url(r'^getMembersWithFunction/', getMembersWithFunction),

    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)/(?P<date_>[\w].+)', getNumberOfPersonsSessions),
    url(r'^getNumberOfPersonsSessions/(?P<person_id>\d+)', getNumberOfPersonsSessions),

    url(r'^getAllQuestions/(?P<date_>[\w].+)', getAllQuestions),
    url(r'^getAllQuestions/', getAllQuestions),
    url(r'^getAllChangesAfter/(?P<person_update_time>[\w].+)/(?P<session_update_time>[\w].+)/(?P<speech_update_time>[\w].+)/(?P<ballots_update_time>[\w].+)/(?P<question_update_time>[\w].+)/(?P<law_update_time>[\w].+)/', getAllChangesAfter),

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

    url(r'^getOrganizatonsByClassification', getOrganizatonsByClassification),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)/(?P<date_>[\w].+)', getOrganizationRolesAndMembers),
    url(r'^getOrganizationRolesAndMembers/(?P<org_id>\d+)', getOrganizationRolesAndMembers),

    url(r'^getNumberOfAllMPAttendedSessions/(?P<date_>[\w].+)', getNumberOfAllMPAttendedSessions), 

    url(r'^getPGsSpeechesIDs/(?P<org_id>\d+)/(?P<date_>[\w].+)', getPGsSpeechesIDs),

    # Votes and Motion URLs
    url(r'^getVotes/(?P<date_>[\w].+)', getVotes),
    url(r'^getVotes/', getVotes),
    url(r'^isVoteOnDay/(?P<date_>[\w].+)', isVoteOnDay),
    url(r'^isVoteOnDay/', isVoteOnDay),
    url(r'^getTags', getTags),
    url(r'^motionOfSession/(?P<id_se>\d+)', motionOfSession),
    url(r'^getBallotsOfMotion/(?P<motion_id>\d+)', getBallotsOfMotion),
    url(r'^getBallotsOfSession/(?P<id_se>\d+)', getBallotsOfSession),

    # Ballots URLs
    url(r'^getAllBallots/(?P<date_>[\w].+)', getAllBallots),
    url(r'^getAllBallots/', getAllBallots),

    url(r'^getBallotsCounterOfPerson/(?P<person_id>\d+)/(?P<date_>[\w].+|)', getBallotsCounterOfPerson),
    url(r'^getBallotsCounterOfPerson/(?P<person_id>\d+)', getBallotsCounterOfPerson),

    url(r'^getBallotsCounterOfParty/(?P<party_id>\d+)/(?P<date_>[\w].+|)', getBallotsCounterOfParty),
    url(r'^getBallotsCounterOfParty/(?P<party_id>\d+)', getBallotsCounterOfParty),

    url(r'^getVotesTable/(?P<date_to>[\w].+|)', getVotesTable),
    url(r'^getVotesTable/', getVotesTable),

    url(r'^getVotesOfSessionTable/(?P<session_id>\d+)/', getVotesOfSessionTable),

    url(r'^getVotesTableExtended/(?P<date_to>[\w].+|)', getVotesTableExtended),
    url(r'^getVotesTableExtended/', getVotesTableExtended),

    # Sessions URLs
    url(r'^getSessions/(?P<date_>[\w].+)', getSessions),
    url(r'^getSessions/', getSessions),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)/(?P<date_>[\w].+)', getSessionsOfOrg),
    url(r'^getSessionsOfOrg/(?P<org_id>\d+)', getSessionsOfOrg),

    # Speech URLs
    url(r'^getAllSpeeches/(?P<date_>[\w].+)', getAllSpeeches),
    url(r'^getAllSpeeches', getAllSpeeches),
    url(r'^isSpeechOnDay/(?P<date_>[\w].+)', isSpeechOnDay),
    url(r'^isSpeechOnDay/', isSpeechOnDay),
    url(r'^getSpeechData/(?P<speech_id>\d+)', getSpeechData),
    url(r'^getAllAllSpeeches/$', getAllAllSpeeches),

    url(r'^getSpeechesOfMP/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeechesOfMP),
    url(r'^getSpeechesOfMP/(?P<person_id>\d+)', getSpeechesOfMP),

    url(r'^getAllMPsSpeeches/(?P<date_>[\w].+)', getAllSpeechesOfMPs),
    url(r'^getAllMPsSpeeches', getAllSpeechesOfMPs),

    url(r'^getSpeeches/(?P<person_id>\d+)/(?P<date_>[\w].+)', getSpeeches),
    url(r'^getSpeeches/(?P<person_id>\d+)', getSpeeches),

    url(r'^getMPSpeechesIDs/(?P<person_id>\d+)/(?P<date_>[\w].+)', getMPSpeechesIDs),

    url(r'^getSpeechesInRange/(?P<person_id>\d+)/(?P<date_from>[\w].+)/(?P<date_to>[\w].+)', getSpeechesInRange),

    # POST save url's for parser
    url(r'^addQuestion/', addQuestion),

    # debug helpers
    url(r'^getMembershipDuplications', getMembershipDuplications),
    url(r'^postMembersFixer', postMembersFixer),
    url(r'^membersFlowInOrg', membersFlowInOrg),
    url(r'^membersFlowInPGs', membersFlowInPGs),
    url(r'^membersFlowInDZ', membersFlowInDZ),
    url(r'^checkSessions/(?P<date_>[\w].+)', checkSessions),

    url(r'^getStrip', getStrip),
    url(r'^getMembershipNetwork', getMembershipNetwork),
    url(r'^getAmendments', getAmendment),

    url(r'^getNumberOfSpeeches', getNumberOfSpeeches),

    # MONITORING
    url(r'^monitoring', monitorMe),
    #url(r'^docs/', include_docs_urls(title='Test Suite API')),
    url(r'^', include(router.urls)),
]
