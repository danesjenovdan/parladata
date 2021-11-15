from django.conf import settings

from parladata.models.memberships import OrganizationMembership

from icu import Collator, Locale


local_collator = Collator.createInstance(Locale(settings.LANGUAGE_CODE))
