#!/bin/bash

sudo docker login rg.fr-par.scw.cloud/djnd -u nologin -p $SCW_SECRET_TOKEN

# BUILD AND PUBLISH PRAVNA MREZA
sudo docker build -f Dockerfile -t parladata:latest .
sudo docker tag parladata:latest rg.fr-par.scw.cloud/djnd/parladata:latest
sudo docker push rg.fr-par.scw.cloud/djnd/parladata:latest
