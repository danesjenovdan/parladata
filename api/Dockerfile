# start with the nodejs image, calling it 'build'
FROM node:alpine as build

# install node modules
COPY package.json yarn.lock /api/

WORKDIR /api

RUN yarn

# build assets
COPY . /api

ENV SOLR_URL=http://solr:8983/solr/parlasearch

CMD node run.js
