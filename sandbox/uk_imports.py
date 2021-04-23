import csv
from datetime import datetime

from parladata.models import Person, Link

def import_personal_data():
    with open('Poslanci.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(reader):
            if i == 0:
                continue
            print(row)
            #poslanec,poslanecLabel,date_of_birth,place_of_birth,place_of_birthLabel,Twitter_username,Facebook_profile_ID,birth_name,honorific_prefix,honorific_prefixLabel,member_of_political_party,member_of_political_partyLabel
            person = Person.objects.filter(name__icontains=row[1])
            if person:
                print("fixing " + row[1])
                person = person[0]
                
                twitter = row[5]
                facebook = row[6]
                if row[2]:
                    date_of_birth = datetime.strptime(row[2].split(' ')[0],'%m/%d/%Y') # 12/9/1960 1:00
                    person.date_of_birth = date_of_birth
                cur_twitter = person.link_set.filter(tags__name__in=['tw'])
                cur_facebook = person.link_set.filter(tags__name__in=['fb'])
                if not cur_twitter and twitter:
                    link = Link(person=person, url='https://twitter.com/' + twitter)
                    link.save()
                    link.tags.add('tw')
                if not cur_facebook and facebook:
                    link = Link(person=person, url='https://facebook.com/' + facebook)
                    link.save()
                    link.tags.add('fb')
                person.save()
            else:
                print("cannot find people")
            
