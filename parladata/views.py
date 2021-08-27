from django.forms import formset_factory
from django.shortcuts import render
from django import forms
from django.contrib import admin

from parladata.forms import MergePeopleForm
from parladata.models.person import Person
from parladata.models.ballot import Ballot
from parladata.models.speech import Speech
from parladata.models.question import Question
from parladata.models.task import Task


def merge_people(request):
    print('merge people')
    passed_real_person = request.GET.get('real_person', None)
    app_list = admin.site.get_app_list(request)
    if request.method == 'POST':
        form = MergePeopleForm(request.POST)
        print(form.data)
        real_person = dict(form.data)['real_person'][0]
        people = dict(form.data)['people']
        confirmed = dict(form.data)['confirmed'][0]
        if people:
            if confirmed:
                Task(
                    name='merge_people',
                    payload={
                        'real_person_id': real_person,
                        'fake_person_ids': people
                    }
                ).save()
                return render(
                    request,
                    'merge_people.html',
                    {
                        'form': MergePeopleForm(),
                        'info': 'People will be merged soon.',
                        'app_list': app_list,
                        'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentmember'}}
                    }
                )

            statisctics = make_statistics(real_person, people)
            print(statisctics)
            _mutable = form.data._mutable
            form.data._mutable = True
            form.data['confirmed'] = True
            form.data._mutable = _mutable
            print(vars(form['people'].field.widget))
            form['real_person'].field.widget = forms.HiddenInput()
            form['people'].field.widget = forms.HiddenInput()
            return render(
                request,
                'merge_people.html',
                {
                    'statistics': statisctics,
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentmember'}}
                }
            )
        else:
            form.clean()
            return render(
                request,
                'merge_people.html',
                {
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentmember'}}
                }
            )

    if passed_real_person:
        form = MergePeopleForm(initial={'real_person': passed_real_person})
    else:
        form = MergePeopleForm()

    return render(
        request,
        'merge_people.html',
        {
            'form': form,
            'app_list': app_list,
            'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentmember'}}
        }
    )


def make_statistics(real_person_id, fake_person_ids):
    data = {}

    real_person = Person.objects.get(id=int(real_person_id))
    data['real_person'] = {
        'name': real_person.name,
        'ballots': real_person.ballots.all().count(),
        'speeches': real_person.speeches.all().count(),
        'authored_questions': real_person.authored_questions.all().count(),
        'received_questions': real_person.received_questions.all().count(),
    }

    data['fake_people'] = []

    fake_people = Person.objects.filter(id__in=fake_person_ids)
    print(fake_people)

    for fake_person in fake_people:
        data['fake_people'].append({
            'name': fake_person.name,
            'ballots': fake_person.ballots.all().count(),
            'speeches': fake_person.speeches.all().count(),
            'authored_questions': fake_person.authored_questions.all().count(),
            'received_questions': fake_person.received_questions.all().count(),
        })

    return data
