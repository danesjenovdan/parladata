echo BEFORE START
/opt/docker-solr/scripts/precreate-core parlasearch
ln -s --force /parlasearch-conf/* /opt/solr/server/solr/mycores/parlasearch/conf/
