FROM solr:7.6.0

COPY ./slolem /opt/solr-slolem
COPY ./parlasearch-conf /parlasearch-conf
COPY ./scripts/create_core.sh /scripts/create_core.sh

ENV LD_LIBRARY_PATH=/opt/solr-slolem/bin

# RUN /opt/docker-solr/scripts/precreate-core parlasearch && \
#     ln -s --force /parlasearch-conf/* /opt/solr/server/solr/mycores/parlasearch/conf/ && \
#     export LD_LIBRARY_PATH=/opt/solr-slolem/bin:$LD_LIBRARY_PATH

EXPOSE 8983
