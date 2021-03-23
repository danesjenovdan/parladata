#!/bin/bash

TAG=latest

sudo docker login rg.fr-par.scw.cloud/djnd -u nologin -p $SCW_SECRET_TOKEN

# BUILD AND PUBLISH API
sudo docker build -f api/Dockerfile -t parlasearch:$TAG api
sudo docker tag parlasearch:$TAG rg.fr-par.scw.cloud/djnd/parlasearch:$TAG
sudo docker push rg.fr-par.scw.cloud/djnd/parlasearch:$TAG

# BUILD AND PUBLISH SOLR
sudo docker build -f solr/Dockerfile -t parlasolr:$TAG solr
sudo docker tag parlasolr:$TAG rg.fr-par.scw.cloud/djnd/parlasolr:$TAG
sudo docker push rg.fr-par.scw.cloud/djnd/parlasolr:$TAG
