const _ = require('lodash');

let config;
const env = process.env.NODE_ENV;

const defaultConfig = {
  port: 3003,
  serverTimeout: 30000,
  urls: {
    cdn: 'https://cdn.parlameter.si/v1/parlassets',
    analize: 'https://analize.parlameter.si/v1',
    // data: 'https://data.parlameter.si/v1',
    // isci: 'https://isci.parlameter.si',
    // glej: 'https://glej.parlameter.si',
    // base: 'https://parlameter.si',
  },
  solrUrl: 'http://localhost:8983/solr/parlasearch',
};

if (env === 'production') {
  // eslint-disable-next-line global-require, import/no-unresolved
  config = require('./production');
} else if (env === 'development') {
  // eslint-disable-next-line global-require, import/no-unresolved
  config = require('./development');
} else {
  // eslint-disable-next-line global-require
  config = require('./sample');
}

module.exports = _.merge({}, defaultConfig, config);
