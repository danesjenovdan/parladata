FROM solr:8.10.0

COPY ./slolem /opt/solr-slolem
COPY ./parlasearch-conf /parlasearch-conf
COPY ./log4j2.xml ./server/resources/log4j2.xml

ENV LD_LIBRARY_PATH=/opt/solr-slolem/bin

ENV SOLR_HOME=/var/solr/data

EXPOSE 8983
