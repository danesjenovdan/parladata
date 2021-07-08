from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group

from parladata.models.vote import Vote
from parladata.models.session import Session
from parladata.models.motion import Motion
from parladata.models.speech import Speech

from datetime import datetime, timedelta

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
                scores[speech_id] = score/len(splitted_title)

            if scores:
                the_speech = max(scores.items(), key=operator.itemgetter(1))[0]
                speech = speeches_with_motion.get(id=the_speech)
                speech.motions.add(motion)
                score = scores[the_speech]
                speech.tags.add(str(int(score*10)*10))

def notify_editors_for_new_data():
    now = datetime.now()
    yeterday = now - timedelta(days=1)

    new_motions = Motion.objects.filter(created_at__gte=yeterday)
    new_speeches = Speech.objects.filter(created_at__gte=yeterday)
    editor_group = Group.objects.filter(name__icontains="editor").first()
    if new_motions or new_speeches:
        for editor in editor_group.user_set.all():
            send_email(
                _('New data for edit in parlameter'),
                editor.email,
                'daily_notification.html',
                {
                    'new_motions': new_motions,
                    'new_speeches': new_speeches
                }
            )

def send_email(subject, to_email, template, data, from_email=settings.FROM_EMAIL):
    html_body = render_to_string(template, data)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=from_email,
        to=[to_email],
        body=text_body)
    msg.attach_alternative(html_body, "text/html")
    msg.send()
