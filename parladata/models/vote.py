from django.db import models

from parladata.behaviors.models import Timestampable, Taggable
from parladata.models.memberships import PersonMembership

class Vote(Timestampable, Taggable):
    """Votings which taken place in parlament."""

    name = models.TextField(
        blank=True,
        null=True,
        help_text='Vote name/identifier'
    )

    motion = models.ForeignKey(
        'Motion',
        blank=True, null=True,
        related_name='vote',
        on_delete=models.CASCADE,
        help_text='The motion for which the vote took place'
    )

    timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Vote time'
    )

    needs_editing = models.BooleanField(
        "Is vote needs editing",
        default=False
    )

    result = models.BooleanField(
        blank=True,
        null=True,
        help_text='The result of the vote'
    )

    def get_option_counts(self, gov_side=None):
        """
        gov_side: is used for getting option counts for coalition and opposition.
        gov_side options:
            * None: all members
            * 'coalition': coalition members
            * 'opposition': members which's not in coalition
        """
        if gov_side == None:
            ballots = self.ballots.all()
        else:
            vote_start_time = self.motion.datetime

            # root org is parliament/municipality
            root_organization = self.motion.session.organizations.first()
            coalition_membership = root_organization.organizationmemberships_children.active_at(
                vote_start_time
            ).filter(
                member__tags__name='coalition'
            ).prefetch_related('member').first()

            # if coalition is not set then return empty dict
            if not coalition_membership:
                return {}
            else:
                coalition = coalition_membership.member
                coalition_groups = coalition.query_organization_members(vote_start_time)
                coalition_voter_ids = PersonMembership.objects.filter(
                    role='voter',
                    on_behalf_of__in=coalition_groups,
                    organization=root_organization,
                ).active_at(vote_start_time).values_list('member_id')

            if gov_side == 'coalition':
                ballots = self.ballots.filter(personvoter_id__in=coalition_voter_ids)
            elif gov_side == 'opposition':
                ballots = self.ballots.exclude(personvoter_id__in=coalition_voter_ids)
            else:
                raise ValueError(f'gov_side can be None, coalition, opposition. You set it to {gov_side}')

        annotated_ballots = ballots.values(
            'option'
        ).annotate(
            option_count=models.Count('option')
        ).order_by('-option_count')

        option_counts = {
            option_sum['option']: option_sum['option_count'] for
            option_sum in annotated_ballots
        }

        # we need this to also show zeroes
        return {
            key: option_counts.get(key, 0) for
            key in ['absent', 'abstain', 'for', 'against'] # TODO get this from global var
        }

    def get_stats(self, gov_side=None):
        """
        gov_side: is used for getting statistics for coalition and opposition.
        gov_side options:
            * None: all members
            * 'coalition': coalition members
            * 'opposition': members which's not in coalition
        """
        option_counts = self.get_option_counts(gov_side)
        if not option_counts:
            return None
        max_option = max(option_counts, key=option_counts.get)
        max_percentage = option_counts.get(max_option, 0) / sum(option_counts.values()) * 100
        return {
            'is_outlier': False, # TODO remove because this is disabled on the front for now.
            'passed': self.motion.result,
            'max_option_percentage': max_percentage,
            'max_option': max_option
        }

    def __str__(self):
        return self.name
