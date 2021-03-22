#!/bin/bash

sudo docker login rg.fr-par.scw.cloud/djnd -u nologin -p $SCW_SECRET_TOKEN

# BUILD AND PUBLISH API
sudo docker build -f api/Dockerfile -t parlasearch:latest api
sudo docker tag parlasearch:latest rg.fr-par.scw.cloud/djnd/parlasearch:latest
sudo docker push rg.fr-par.scw.cloud/djnd/parlasearch:latest

# BUILD AND PUBLISH SOLR
sudo docker build -f solr/Dockerfile -t parlasolr:latest solr
sudo docker tag parlasolr:latest rg.fr-par.scw.cloud/djnd/parlasolr:latest
sudo docker push rg.fr-par.scw.cloud/djnd/parlasolr:latest
