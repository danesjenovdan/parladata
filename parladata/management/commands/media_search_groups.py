from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from eventregistry import *

from parladata.models import Medium, Organization
from parladata.models.media import MediaReport
from parladata.models.versionable_properties import OrganizationAcronym, OrganizationName

from datetime import datetime, timedelta


def domain_from_url(url):
    return url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]

def get_media_uris():
    media_urls = Medium.objects.filter(active=True).values('id', 'url')
    return { domain_from_url(x['url']): x['id'] for x in media_urls }

def get_groups(timestamp=datetime.now()):
    playing_field = Organization.objects.first() # FIXME: dont hardcode this
    groups = playing_field.query_parliamentary_groups(timestamp)
    return groups


class Command(BaseCommand):
    help = 'Search media for reports about groups'

    def handle(self, *args, **options):
        self.stdout.write('Start media search for groups ...')

        timestamp = datetime.now()

        # get active media uris
        media_uri_to_id = get_media_uris()
        media_uris = list(media_uri_to_id.keys())
        self.stdout.write(f'Got {len(media_uris)} media urls')

        # get active groups
        groups = get_groups(timestamp)
        group_count = len(groups)
        self.stdout.write(f'Got {group_count} groups')

        # login to event registry
        er = EventRegistry(apiKey=settings.EVENT_REGISTRY_API_KEY)

        for i, group in enumerate(groups):
            self.stdout.write(f'[{i+1}/{group_count}] Querying articles for {group.name}')

            query = QueryArticlesIter(
                sourceUri=QueryItems.OR(media_uris),
                lang=QueryItems.OR([settings.EVENT_REGISTRY_LANGUAGE_CODE]),
                isDuplicateFilter='skipDuplicates',
                keywords=QueryItems.OR([group.name, group.acronym]),
                dateStart=timestamp - timedelta(days=7),
            )

            results = query.execQuery(
                er,
                sortBy="date",
                returnInfo=ReturnInfo(articleInfo=ArticleInfoFlags(body=False)),
                # maxItems=10,
            )

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

                report.mentioned_organizations.add(group.id)

        self.stdout.write('Done')
