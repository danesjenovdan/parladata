su solr -c "rm /var/solr/data/parlasearch/conf/managed-schema"
su solr -c "ln -s --force /home/parladaddy/parlasearch/solr/parlasearch-conf/* /var/solr/data/parlasearch/conf/"

