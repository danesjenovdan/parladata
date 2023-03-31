from django.core.management.base import BaseCommand

from parladata.models.session import Session
from parladata.models.organization import Organization
from parladata.models.common import Mandate
from parladata.models.question import Question
from parladata.models.legislation import Law
from parladata.models.speech import Speech
from parladata.models.memberships import PersonMembership, OrganizationMembership

from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Prepare database for tests (delete data)'

    """
    * import_db.sh (import mol databse)
        * copy database
        * load database
    * python manage.py prepare_test_database
    * python manage.py migrate parlacards zero
    * python manage.py migrate
    * python manage.py run_all_analyses --start_time 2022-11-30
    * python manage.py dumpdata -e contenttypes -e auth.permission -o tests/fixtures/test_db.json
    """

    def handle(self, *args, **options):
        # delete sessions
        Session.objects.all().exclude(id__in=[3783, 3782, 4280, 4283]).delete()

        mandate1 = Mandate.objects.get(id=1)
        mandate1.save()

        mandate2 = Mandate.objects.get(id=2)

        mol2 = Organization.objects.get(id=48)
        sd = Organization.objects.get(id=19)
        svoboda = Organization.objects.get(id=52)

        # move sd memberships to another group for mandate 2
        PersonMembership.objects.filter(organization=sd, mandate=mandate2).update(organization=svoboda)
        PersonMembership.objects.filter(on_behalf_of=sd, mandate=mandate2).update(on_behalf_of=svoboda)
        OrganizationMembership.objects.filter(organization=mol2, member=sd).delete()

        Speech.objects.filter(session_id__in=[4280, 4283]).delete()
