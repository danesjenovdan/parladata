from parladata.models import Vote, Session
from django.db.models import Count


def checkDuplVotes():
    ss = Session.objects.filter(organization_id=95)
    for s in ss:
        vv = s.vote_set.all()
        dupls = vv.values('start_time').annotate(Count('id')).order_by().filter(id__count__gt=1)
        if dupls:
            print vv.count()
            print s
            uniq = list(set([d['start_time'] for d in dupls]))
            print len(uniq)
            for dupl in uniq:
                dd = vv.filter(start_time=dupl)
                print 'is_equal_result', dd[0].getResult() == dd[1].getResult()
                print 'Text', dd[0].name == dd[1].name
