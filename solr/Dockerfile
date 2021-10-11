FROM solr:8.10.0

COPY ./slolem /opt/solr-slolem
COPY ./parlasearch-conf /parlasearch-conf

ENV LD_LIBRARY_PATH=/opt/solr-slolem/bin

EXPOSE 8983
