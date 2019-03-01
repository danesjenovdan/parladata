const _ = require('lodash');

let config;
const env = process.env.NODE_ENV;

const defaultConfig = {
  port: 7003,
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
  tfidf: {
    blacklist: ['a', 'pa', 'toda', 'vendar', 'ampak', 'ako', 'če', 'kadar', 'čeprav', 'akoprav', 'akoravno', 'akotudi', 'ali', 'Vendar', 'bodi', 'bodisi', 'ko', 'ker', 'čeravno', 'četudi', 'čim', 'da', 'ne', 'bi', 'bili', 'v', 'katere', 'dasi', 'dasiprav', 'dasiravno', 'dasitudi', 'dočim', 'medtem', 'dokler', 'doklič', 'drugače', 'sicer', 'ergo', 'torej', 'in', 'kajti', 'kakor', 'ki', 'kot', 'kolikor', 'komaj', 'takoj', 'le', 'ma', 'magari', 'naj', 'najsi', 'najsibo', 'namreč', 'navrh', 'marveč', 'temveč', 'niti', 'odklej', 'od', 'kdaj', 'odnosno', 'oziroma', 'potem', 'preden', 'predno', 'saj', 'samo', 'tako', 'tedaj', 'tem', 'ter', 'zato', 'to', 'je', 'vendarle', 'zakaj', 'za', 'so', 'na', 'se', 'biti', 'si', 'po', 'še', 'ta', 'do', 'iz', 'ni', 'bo', 'že', 'kar', 'pri', 'tudi', 'ti', 'me'],
  },
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
