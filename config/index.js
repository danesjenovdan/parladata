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
    blacklist: ['ako', 'akoprav', 'akoravno', 'akotudi', 'ali', 'ampak', 'bi', 'bili', 'biti', 'bo', 'bodi', 'bodisi', 'bom', 'bržkone', 'če', 'čeprav', 'čeravno', 'četudi', 'čim', 'da', 'danes', 'dasi', 'dasiprav', 'dasiravno', 'dasitudi', 'del', 'do', 'dober', 'dočim', 'dokler', 'doklič', 'dosti', 'drag', 'drug', 'drugače', 'ergo', 'ga', 'glede', 'gor', 'gotovo', 'hvala', 'ima', 'in', 'iz', 'jaz', 'je', 'kadar', 'kaj', 'kajti', 'kak', 'kakor', 'kakšen', 'kar', 'katere', 'kdaj', 'kdo', 'ker', 'ki', 'ko', 'kolikor', 'komaj', 'kot', 'le', 'lep', 'ma', 'magari', 'malce', 'mali', 'marveč', 'me', 'med', 'medtem', 'mi', 'morda', 'na', 'naj', 'najbrž', 'najsi', 'najsibo', 'namreč', 'navrh', 'navsezadnje', 'nazadnje', 'ne', 'nek', 'nekaj', 'nekakšen', 'nekateri', 'nekdo', 'nekje', 'ni', 'nikdar', 'niti', 'no', 'notri', 'očiten', 'od', 'odklej', 'odnosno', 'ogromen', 'ozir', 'oziroma', 'pa', 'pač', 'po', 'pol', 'potem', 'potlej', 'pravzaprav', 'preden', 'predno', 'pri', 'priti', 'res', 'saj', 'sam', 'samo', 'se', 'sem', 'seveda', 'si', 'sicer', 'skupaj', 'smo', 'so', 'spet', 'ste', 'svoj', 'še', 'ta', 'tak', 'tako', 'takoj', 'takrat', 'tale', 'te', 'tedaj', 'teh', 'tem', 'temveč', 'ter', 'ti', 'tisti', 'to', 'toda', 'tolik', 'torej', 'tudi', 'tukaj', 'tule', 'vaš', 'vem', 'vendar', 'vendarle', 'verjetneje', 'ves', 'vi', 'vir', 'vse', 'vseeno', 'vsi', 'za', 'zakaj', 'zame', 'zato', 'zdaj', 'zdi', 'zelo', 'znotraj', 'že'],
  },
  facetRangeStart: '2014-01-01',
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
