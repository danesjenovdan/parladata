FROM solr:7.6.0

COPY ./slolem /opt/solr-slolem
COPY ./parlasearch-conf /parlasearch-conf

ENV LD_LIBRARY_PATH=/opt/solr-slolem/bin

RUN chown 8983:8983 /opt/solr/server/solr/mycores

# RUN /opt/docker-solr/scripts/precreate-core parlasearch && \
#     ln -s --force /parlasearch-conf/* /opt/solr/server/solr/mycores/parlasearch/conf/ && \
#     export LD_LIBRARY_PATH=/opt/solr-slolem/bin:$LD_LIBRARY_PATH

EXPOSE 8983
