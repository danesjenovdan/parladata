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
      'hl.fl': 'content_t',
      'hl.fragmenter': 'regex',
      'hl.regex.pattern': '\\w[^\\.!\\?]{1,600}[\\.!\\?]',
      'hl.fragsize': '5000',
      'hl.mergeContiguous': false,
      'hl.snippets': 1,
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
  const { responseHeader, ...json } = await resp.json();
  return json;
}

function fixQuery(q) {
  return q.replace(/\bIN\b/g, 'AND').replace(/\B!\b/g, '+');
}

async function search(req, res) {
  const q = fixQuery(req.query.q || '');
  const startPage = Number(req.query.page) || 0;

  const json = await solrSelect({
    highlight: true,
    facet: true,
  }, {
    fq: 'tip_t:govor',
    q: `content_t:(${q})`,
    start: startPage * ROWS_PER_PAGE,
  });

  res.json(json);
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
  search: wrap(search),
  refetchData,
};
