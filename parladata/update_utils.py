from django.db.models import Q

from parladata.models import Vote

import operator


"""
relativno navadno večino: (večina prisotnih poslancev; najpogostejši način odločanja),
absolutno navadno večino: (vsaj 46 glasov poslancev),
relativno kvalificirano večino: (2/3 prisotnih poslancev) ali
absolutno kvalificirano večino: (vsaj 60 glasov poslancev).
"""

def get_result_for_relative_normal_majority(self, vote):
    options = vote.get_option_counts()
    return options['for'] > options['against']

def get_result_for_absolute_normal_majority(self, vote):
    options = vote.get_option_counts()
    return options['for'] > (sum(options.values())/2 + 1)

def set_results_to_votes(majority='relative_normal'):
    for vote in Vote.objects.filter(result=None):
        if majority == 'absolute_normal':
            final_result = self.get_result_for_absolute_normal_majority(vote)
        else:
            final_result = self.get_result_for_relative_normal_majority(vote)

        motion = vote.motion
        motion.result = final_result
        motion.save()
        vote.result = final_result
        vote.save()


def pair_motions_with_speeches():
    for session in Session.objects.all():
        motions = session.motions.filter(speech=None)
        speeches_with_motion = session.speeches.filter(Q(content__contains='PROTI'), Q(content__contains='ZA'))
        contents = {speech.id: speech.content for speech in speeches_with_motion}
        for motion in motions:
            title = motion.title
            splitted_title = title.split(" ")
            scores = {}
            for speech_id, content in contents.items():
                score = 0.0
                for word in splitted_title:
                    if word in content:
                        score +=1
                scores[speech_id] = score/len(c)

            the_speech = max(scores.items(), key=operator.itemgetter(1))[0]
            print(the_speech)
            speech = speeches_with_motion.get(id=the_speech)
            speech.motions.add(motion)

