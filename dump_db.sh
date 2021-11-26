#!/bin/bash

PGPASSWORD=Q893DMKuSY \
    pg_dump -U postgres \
        -f db.dump \
        -d \
        parladata-ua \
        -p 44267 \
        -h localhost

# echo
# echo "Downloading from S3"
# # copy dump from s3
# aws s3 cp s3://djnd-backups/${DUMP_FILE_NAME} . \
#     --endpoint-url=https://s3.fr-par.scw.cloud \
#     --region=fr-par

# echo
# echo "Decrypting file"
# # decrypt file
# # mcrypt -d ${DUMP_FILE_NAME} -k $DB_BACKUP_PASSWORD
# openssl aes-256-ecb -d -nopad -in ${DUMP_FILE_NAME} -out db.pgdump -k $DB_BACKUP_PASSWORD

# echo
# echo "Decompressing file"
# # decompress
# bzip2 -d ${DUMP_FILE_NAME}
