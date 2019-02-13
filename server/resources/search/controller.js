const querystring = require('querystring');
const fetch = require('node-fetch');
const data = require('../../data');
const config = require('../../../config');

const wrap = fn => (req, res, next) => fn(req, res, next).catch((error) => {
  res.status(500).json({
    error: true,
    status: 500,
    message: String(error),
  });
});

const ROWS_PER_PAGE = 10;

function fixResponse(json) {
  if (json.response && json.response.docs) {
    json.response.docs.forEach((doc) => {
      // eslint-disable-next-line no-underscore-dangle
      delete doc._version_;

      Object.keys(doc)
        .filter(key => key.endsWith('_json'))
        .forEach((key) => {
          doc[key.slice(0, -5)] = JSON.parse(doc[key]);
          delete doc[key];
        });
    });

    if (json.highlighting) {
      Object.keys(json.highlighting)
        .forEach((key) => {
          const val = json.highlighting[key];
          const hl = Array.isArray(val.content) ? val.content.join(' … ') : val.content;
          const doc = json.response.docs.find(d => d.id === key);
          if (doc) {
            doc.content_hl = hl;
          }
        });
    }
  }
  return json;
}

async function solrSelect({ highlight = false, facet = false } = {}, params) {
  // 'sort': 'datetime_dt desc',

  const defaults = {
    wt: 'json',
    // debugQuery: true,

    rows: ROWS_PER_PAGE,
    start: 0,
  };

  if (highlight) {
    Object.assign(defaults, {
      'hl': true,
      'hl.fl': 'content',
      'hl.method': 'unified',
      // 'hl.fragmenter': 'regex',
      // 'hl.regex.pattern': '\\w[^\\.!\\?]{1,600}[\\.!\\?]',
      // 'hl.fragsize': '5000',
      // 'hl.mergeContiguous': false,
      // 'hl.snippets': 1,
    });
  }

  if (facet) {
    Object.assign(defaults, {
      'facet': true,
      'facet.field': ['speaker_i', 'party_i'],
      'facet.range': 'datetime_dt',
      'facet.range.start': '2014-01-01T00:00:00.000Z', // TODO: different start time based on country
      'facet.range.gap': '+1MONTHS',
      'facet.range.end': 'NOW',
    });
  }

  Object.assign(defaults, params);

  const url = `${config.solrUrl}/select`;
  const qs = querystring.stringify(defaults);

  const resp = await fetch(`${url}?${qs}`);
  const json = await resp.json();

  return fixResponse(json);
}

function fixQuery(q) {
  return String(q).replace(/\bIN\b/g, 'AND').replace(/\B!\b/g, '+');
}

function search(type) {
  return async (req, res) => {
    const query = req.query.q.trim();
    if (!query) {
      res.status(400).json({
        error: true,
        status: 400,
        message: 'Invalid query',
      });
      return;
    }

    const q = fixQuery(query || '');
    const startPage = Number(req.query.page) || 0;

    const solrJson = await solrSelect({
      highlight: true,
      facet: true,
    }, {
      fq: `type:${type}`,
      q: `content:(${q}) OR title:(${q})`,
      start: startPage * ROWS_PER_PAGE,
    });

    if (solrJson.error) {
      const status = solrJson.error.code || solrJson.responseHeader.status || 0;
      res.status(status).json({
        error: true,
        status,
        message: solrJson.error.msg,
      });
      return;
    }

    res.json({
      query: req.query.q,
      response: solrJson.response,
      facet_counts: solrJson.facet_counts,
    });
  };
}

function refetchData(req, res) {
  Promise.resolve()
    .then(() => data.refetch())
    .then((error) => {
      if (!error) {
        res.json({
          ok: true,
          message: 'Finished refetch',
        });
      } else {
        res.json({
          ok: false,
          message: 'Failed refetch',
          error,
        });
      }
    });
}

module.exports = {
  searchSpeeches: wrap(search('speech')),
  searchVotes: wrap(search('vote')),
  searchLegislation: wrap(search('legislation')),
  refetchData,
};
