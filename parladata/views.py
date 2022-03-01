from django.forms import formset_factory
from django.shortcuts import render, redirect
from django import forms
from django.contrib import admin
from django.urls import reverse

from parladata.forms import MergePeopleForm, AddBallotsForm, AddAnonymousBallotsForm, MergeOrganizationsForm
from parladata.utils import make_person_merge_statistics, make_organization_merge_statistics
from parladata.models.person import Person
from parladata.models.ballot import Ballot
from parladata.models.speech import Speech
from parladata.models.vote import Vote
from parladata.models.question import Question
from parladata.models.task import Task
from parladata.models.common import Mandate
from parladata.models.organization import Organization

import collections


# TODO maybe require login?
def merge_people(request):
    print('merge people')
    passed_real_person = request.GET.get('real_person', None)
    app_list = admin.site.get_app_list(request)
    if request.method == 'POST':
        form = MergePeopleForm(request.POST)
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

            statisctics = make_person_merge_statistics(real_person, people)
            _mutable = form.data._mutable
            form.data._mutable = True
            form.data['confirmed'] = True
            form.data._mutable = _mutable
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


def merge_organizations(request):
    print('merge organization')
    passed_real_organization = request.GET.get('real_organization', None)
    app_list = admin.site.get_app_list(request)
    if request.method == 'POST':
        form = MergeOrganizationsForm(request.POST)
        real_organization = dict(form.data)['real_organization'][0]
        organizations = dict(form.data)['organizations']
        confirmed = dict(form.data)['confirmed'][0]
        if organizations:
            if confirmed:
                Task(
                    name='merge_organizations',
                    payload={
                        'real_org_id': real_organization,
                        'fake_orgs_ids': organizations
                    }
                ).save()
                return render(
                    request,
                    'merge_organizations.html',
                    {
                        'form': MergeOrganizationsForm(),
                        'info': 'organizations will be merged soon.',
                        'app_list': app_list,
                        'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentarygroup'}}
                    }
                )

            statisctics = make_organization_merge_statistics(real_organization, organizations)
            _mutable = form.data._mutable
            form.data._mutable = True
            form.data['confirmed'] = True
            form.data._mutable = _mutable
            return render(
                request,
                'merge_organizations.html',
                {
                    'statistics': statisctics,
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentarygroup'}}
                }
            )
        else:
            form.clean()
            return render(
                request,
                'merge_organizations.html',
                {
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentarygroup'}}
                }
            )

    if passed_real_organization:
        form = MergeOrganizationsForm(initial={'real_organization': passed_real_organization})
    else:
        form = MergeOrganizationsForm()

    return render(
        request,
        'merge_organizations.html',
        {
            'form': form,
            'app_list': app_list,
            'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'parliamentarygroup'}}
        }
    )


def add_ballots(request):
    # TODO this dies if the vote doesn't have a date
    app_list = admin.site.get_app_list(request)
    if request.method == 'POST':
        vote_id = request.GET.get('vote_id', None)
        vote = Vote.objects.get(id=vote_id)
        if not vote:
            return redirect(reverse("admin:parladata_vote_changelist"))
        form = AddBallotsForm(request.POST)
        print(form.data)
        people_for = dict(form.data).get('people_for', [])
        people_against = dict(form.data).get('people_against', [])
        people_abstain = dict(form.data).get('people_abstain', [])
        people_absent = dict(form.data).get('people_absent', [])
        people_did_not_vote = dict(form.data).get('people_did_not_vote', [])
        confirmed = dict(form.data)['confirmed'][0]
        edit = dict(form.data)['edit'][0]

        # v=Vote.objects.get(id=9401)
        # all_members = os.query_members_by_role(role='voter', timestamp=v.timestamp)
        # non_absent_voters = v.ballots.values_list('personvoter', flat=True)
        # absent_people = all_members.exclude(id__in=non_absent_voters)

        # for person in absent_people:
        #     Ballot(vote=v, personvoter=person,option='absent').save()

        if people_for or people_against or people_abstain or people_absent or people_did_not_vote:
            root_org = Mandate.objects.last().query_root_organizations(timestamp=vote.timestamp)[1] # TODO this is horribly hardcoded
            people_with_ballots = people_for + people_against + people_abstain + people_absent + people_did_not_vote
            all_members = root_org.query_members_by_role(role='voter', timestamp=vote.timestamp)
            auto_absent_people = all_members.exclude(id__in=people_with_ballots)
            print(confirmed, type(confirmed))
            if confirmed == 'True':
                auto_absent_people_ids = list(auto_absent_people.values_list('id', flat=True))
                options = {
                    'for': people_for,
                    'against': people_against,
                    'abstain': people_abstain,
                    'absent': people_absent + auto_absent_people_ids,
                    'did not vote': people_did_not_vote,
                }
                for option, people in options.items():
                    print(option, people)
                    Ballot.objects.bulk_create([
                        Ballot(
                            personvoter_id=person,
                            option=option,
                            vote=vote)
                        for person in people if person
                    ])

                return redirect(reverse("admin:parladata_vote_changelist"))

            ballots = []
            people_with_ballots = people_for + people_against + people_abstain + people_absent + people_did_not_vote
            duplicates = [item for item, count in collections.Counter(people_with_ballots).items() if count > 1]
            duplicated = Person.objects.filter(id__in=duplicates)
            confirm = False
            if not duplicated:
                _mutable = form.data._mutable
                form.data._mutable = True
                form.data['confirmed'] = True
                form.data._mutable = _mutable
                confirm = True

            return render(
                request,
                'add_ballots.html',
                {
                    'ballots': {
                        'people_for': Person.objects.filter(id__in=people_for),
                        'people_against': Person.objects.filter(id__in=people_against),
                        'people_abstain': Person.objects.filter(id__in=people_abstain),
                        'people_absent': Person.objects.filter(id__in=people_absent),
                        'people_did_not_vote': Person.objects.filter(id__in=people_did_not_vote),
                        'people_without_ballot': auto_absent_people,
                        'sum': len(people_with_ballots),
                        'duplicated': duplicated
                    },
                    'form': form,
                    'confirm': confirm,
                    'edit': True if edit == 'True' else False,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'vote'}}
                }
            )
        else:
            form.clean()
            print('cleand form')
            return render(
                request,
                'add_ballots.html',
                {
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'vote'}}
                }
            )

    form = AddBallotsForm()
    print('empty form')

    return render(
        request,
        'add_ballots.html',
        {
            'form': form,
            'app_list': app_list,
            'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'vote'}}
        }
    )

def add_anonymous_ballots(request):
    # TODO this dies if the vote doesn't have a date
    app_list = admin.site.get_app_list(request)
    if request.method == 'POST':
        vote_id = request.GET.get('vote_id', None)
        vote = Vote.objects.get(id=vote_id)
        if not vote:
            return redirect(reverse("admin:parladata_vote_changelist"))
        form = AddAnonymousBallotsForm(request.POST)
        form.is_valid()
        people_for = form.cleaned_data.get('people_for', 0)
        people_against = form.cleaned_data.get('people_against', 0)
        people_abstain = form.cleaned_data.get('people_abstain', 0)
        people_absent = form.cleaned_data.get('people_absent', 0)
        people_did_not_vote = form.cleaned_data.get('people_did_not_vote', 0)
        edit = dict(form.data)['edit'][0]

        if people_for or people_against or people_abstain or people_absent or people_did_not_vote:
            root_org = Mandate.objects.last().query_root_organizations(timestamp=vote.timestamp)[1] # TODO this is horribly hardcoded
            options = {
                'for': people_for,
                'against': people_against,
                'abstain': people_abstain,
                'absent': people_absent,
                'did not vote': people_did_not_vote,
            }
            for option, people in options.items():
                print(option, people)
                Ballot.objects.bulk_create([
                    Ballot(
                        option=option,
                        vote=vote
                    )
                    for i in range(people)
                ])

            return redirect(reverse("admin:parladata_vote_changelist"))

        else:
            form.clean()
            print('cleand form')
            return render(
                request,
                'add_anonymous_ballots.html',
                {
                    'form': form,
                    'app_list': app_list,
                    'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'vote'}}
                }
            )

    form = AddAnonymousBallotsForm()
    print('empty form')

    return render(
        request,
        'add_anonymous_ballots.html',
        {
            'form': form,
            'app_list': app_list,
            'opts': {'app_label': 'parladata', 'app_config': {'verbose_name': 'vote'}}
        }
    )
