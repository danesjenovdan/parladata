from parlacards.serializers.common import CardSerializer

from parlacards.solr import parse_search_query_params, solr_select


class WordGroupsCardSerializer(CardSerializer):
    def get_results(self, person):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        # we are using a single parameter called words
        # which contains the words separated by a comma
        words = self.context.get('GET', {}).get('words', '')

        # if no words were supplied, return an empty response
        if not words:
            return {
                **parent_data,
                'results': [],
            }

        # we join all the words with a space, which should work
        # as an "OR" when querying SOLR
        text_query = ' '.join(
            [word.strip() for word in words.split(',')]
        )

        result = solr_select(text_query=text_query, facet=True)
        
        # solr returns facets in a strange format
        # it's an array of values:
        # the first, third, fifht etc. are strings and represent our people/party ids
        # the second, fourth, sicth etc. are integers and represent the counts
        #
        # that's why we iterate through the arrays/lists and generate a dictionary
        # where the key is the person/party id and the value is the count

        # create the person facet count dictionary
        people_facet_counts = result['facet_counts']['facet_fields']['person_id']
        people_results = {}
        for i in range(int(len(people_facet_counts) / 2)):
            person_index = 2 * i
            count_index = 2 * i + 1
            people_results[people_facet_counts[person_index]] = people_facet_counts[count_index]

        # create the party facet count dictionary
        party_facet_counts = result['facet_counts']['facet_fields']['party_id']
        party_results = {}
        for i in range(int(len(party_facet_counts) / 2)):
            party_index = 2 * i
            count_index = 2 * i + 1
            party_results[party_facet_counts[party_index]] = party_facet_counts[count_index]

        return {
            **parent_data,
            'results': {
                'number_of_speeches': result['response']['numFound'],
                'people': people_results,
                'groups': party_results,
            },
        }