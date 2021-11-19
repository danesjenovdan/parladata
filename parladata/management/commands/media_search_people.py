from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from eventregistry import *

from parladata.models import Medium, Organization
from parladata.models.media import MediaReport
from parladata.models.versionable_properties import PersonName

from datetime import datetime, timedelta


def domain_from_url(url):
    return url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]

def get_media_uris():
    media_urls = Medium.objects.filter(active=True).values('id', 'url')
    return { domain_from_url(x['url']): x['id'] for x in media_urls }

def get_person_names(timestamp=datetime.now()):
    playing_field = Organization.objects.first() # FIXME: dont hardcode this
    people = playing_field.query_voters(timestamp)
    person_names = PersonName.objects.valid_at(timestamp) \
        .filter(owner__in=people) \
        .order_by('owner', '-valid_from') \
        .distinct('owner') \
        .values('owner', 'value')
    return { x['value']: x['owner'] for x in person_names }


class Command(BaseCommand):
    help = 'Search media for reports about people'

    def handle(self, *args, **options):
        self.stdout.write('Start media search for people ...')

        timestamp = datetime.now()

        # get active media uris
        media_uri_to_id = get_media_uris()
        media_uris = list(media_uri_to_id.keys())
        print(media_uris)
        self.stdout.write(f'Got {len(media_uris)} media urls')

        # get active voter names
        person_name_to_id = get_person_names(timestamp)
        person_names = list(person_name_to_id.keys())
        print(person_names)
        self.stdout.write(f'Got {len(person_names)} person names')

        # login to event registry
        er = EventRegistry(apiKey=settings.EVENT_REGISTRY_API_KEY)

        for person_name in person_names:
            self.stdout.write(f'Querying articles for {person_name}')

            query = QueryArticlesIter(
                sourceUri=QueryItems.OR(media_uris),
                lang=QueryItems.OR([settings.EVENT_REGISTRY_LANGUAGE_CODE]),
                isDuplicateFilter='skipDuplicates',
                keywords=person_name,
                dateStart=timestamp - timedelta(days=7),
            )

            results = query.execQuery(
                er,
                sortBy="date",
                returnInfo=ReturnInfo(articleInfo=ArticleInfoFlags(body=False)),
                # maxItems=10,
            )

            person_id = person_name_to_id[person_name]

            count = 0
            for result in results:
                count += 1

                article_uri = result.get('uri')
                article_title = result.get('title')
                article_url = result.get('url')
                article_date = result.get('date')
                medium_uri = result.get('source', {}).get('uri')
                medium_id = media_uri_to_id[medium_uri] if medium_uri in media_uri_to_id else None

                self.stdout.write(f"{count} {article_uri} {article_title}")

                report = MediaReport.objects.filter(uri=article_uri).first()
                if not report:
                    report = MediaReport.objects.create(
                        uri=article_uri,
                        title=article_title,
                        url=article_url,
                        report_date=article_date,
                        retrieval_date=timestamp,
                        medium_id=medium_id,
                    )

                report.mentioned_people.add(person_id)

        self.stdout.write('Done')
