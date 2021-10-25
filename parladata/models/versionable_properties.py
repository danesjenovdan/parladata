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
    EDUCATION_LEVELS = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6/1', '6/1'),
        ('6/2', '6/2'),
        ('7', '7'),
        ('8/1', '8/1'),
        ('8/2', '8/2')

    ]
    value = models.TextField(
        blank=False,
        null=False,
        choices=EDUCATION_LEVELS
    )

class PersonNumberOfMandates(PersonVersionableProperty):
    value = models.IntegerField(blank=False, null=False)

class PersonEmail(PersonVersionableProperty):
    pass

class PersonPreferredPronoun(PersonVersionableProperty):
    PRONOUNS = [
        ('he', 'he'),
        ('she', 'she'),
        ('they', 'they'),
    ]
    value = models.TextField(blank=False, null=False, choices=PRONOUNS)

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

class OrganizationEmail(OrganizationVersionableProperty):
    pass
