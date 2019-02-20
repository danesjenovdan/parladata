BASEDIR=$(dirname "$BASH_SOURCE")

su solr -c "rm /var/solr/data/parlasearch/conf/managed-schema"
su solr -c "ln -s --force $BASEDIR/../parlasearch-conf/* /var/solr/data/parlasearch/conf/"

# link slolem to common directory
ln -s --force $BASEDIR/../slolem /opt/solr-slolem

# append to file
LINE='SOLR_OPTS="$SOLR_OPTS -Djava.library.path=/opt/solr-slolem/bin"'
FILE=/etc/default/solr.in.sh
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
