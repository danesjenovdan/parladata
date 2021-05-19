from django.db import models

from parladata.behaviors.models import VersionableProperty

class PersonVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        'parladata.Person',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True

class PersonName(PersonVersionableProperty):
    pass

class PersonHonorificPrefix(PersonVersionableProperty):
    pass

class PersonHonorificSuffix(PersonVersionableProperty):
    pass

class PersonPreviousOccupation(PersonVersionableProperty):
    pass

class PersonEducation(PersonVersionableProperty):
    pass

class PersonEducationLevel(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)

class PersonNumberOfMandates(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)

class PersonEmail(PersonVersionableProperty):
    pass

class PersonPreferredPronoun(PersonVersionableProperty):
    # TODO make this a selection
    # he
    # she
    # they
    pass

class PersonNumberOfVoters(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)

class PersonNumberOfPoints(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)

# ORGANIZATION

class OrganizationVersionableProperty(VersionableProperty):
    owner = models.ForeignKey(
        'parladata.Organization',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True

class OrganizationName(OrganizationVersionableProperty):
    pass

class OrganizationAcronym(OrganizationVersionableProperty):
    pass
