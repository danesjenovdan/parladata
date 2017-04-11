from parladata.models import Speech, Session, Motion, Vote, Link

from django.core.mail import send_mail
from django.db.models import Count
from django.conf import settings


def testDocumentsLinks():

    motionsWithoutLink = []

    motions = Motion.objects.all()
    for motion in motions:
        mCount = motion.links.all().count()
        if mCount == 0:
            motionsWithoutLink.append(motion.id)

    if motionsWithoutLink:
        send_mail(
            'Motions without documents',
            'Motions without documents: \n' + str(motionsWithoutLink),
            'filip@parlameter.si',
            [admin[1] for admin in settings.ADMINS],
            fail_silently=False,
        )

    return "Test fail" if motionsWithoutLink else "Test pass"


def testDuplSpeeches():
    sk = Session.objects.filter(name__icontains="skupna seja")
    s = Speech.getValidSpeeches(datetime.now()).filter(session__in=sk)
    dups = (s.values('order', 'speaker_id', 'start_time')
            .annotate(count=Count('id'))
            .values('order', 'speaker_id', 'start_time')
            .order_by()
            .filter(count__gt=1)
            )
    duplications = []
    sessions = []
    for d in dups:
        multi = s.filter(start_time=d["start_time"],
                         order=d["order"],
                         speaker_id=d["speaker_id"]).order_by("valid_from")

    duplications.append(multi.values_list("id"))
    dupl_session = list(multi.values_list("session_id"))
    dupl_session.sort()
    sessions.append(dupl_session)

    unique_pairs = [list(x) for x in set(tuple(x) for x in sessions)]

    if duplications:
        send_mail('Speech duplications',
                  'Speech duplications: \n' + str(duplications),
                  'test@parlameter.si',
                  [admin[1] for admin in settings.ADMINS],
                  fail_silently=False,)

        return "Test fail" if motionsWithoutLink else 'Test pass'


def speechesOnSessionTest():
    mails = [admin[1] for admin in settings.ADMINS]# + settings.PARSER_ADMINS]
    data = []
    for s in Session.objects.all().order_by('organization_id'):
        if not s.speech_set.all():
            data.append({'id': s.id,
                         'date': s.start_time,
                         'name': s.name,
                         'org_name': s.organization.name})

    mail_text = 'Sessions without Speeches: \n'
    for s in data:
        mail_text += str(s) + '\n'

    if data:
        send_mail('Sessions without Speeches',
                  'Sessions without Speeches: \n' + mail_text,
                  'test@parlameter.si',
                  mails,
                  fail_silently=False,)
