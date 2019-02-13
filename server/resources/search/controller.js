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
  const defaults = {
    wt: 'json',
    sort: 'start_time desc',
    rows: ROWS_PER_PAGE,
    start: 0,
  };

  if (highlight) {
    Object.assign(defaults, {
      'hl': true,
      'hl.fl': 'content',
      'hl.method': 'unified',
      'hl.fragsize': '400',
    });
  }

  if (facet) {
    Object.assign(defaults, {
      'facet': true,
      'facet.field': ['speaker_i', 'party_i'],
      'facet.range': 'start_time',
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
  return String(q).replace(/\bIN\b/g, 'AND').replace(/\B!\b/g, '+').trim() || '*';
}

function getFilters(type, qp) {
  const response = {
    filters: {},
  };
  const fq = [];
  if (type === 'speech') {
    if (qp.people) {
      const people = qp.people.split(',').map(Number).filter(Boolean);
      response.filters.people = people;
      fq.push(`person_id:(${people.join(' OR ')})`);
      if (people.length === 1) {
        const person = data.staticData.persons[String(people[0])];
        if (person) {
          response.person = person;
        }
      }
    }
    if (qp.parties) {
      const parties = qp.parties.split(',').map(Number).filter(Boolean);
      response.filters.parties = parties;
      fq.push(`party_id:(${parties.join(' OR ')})`);
      if (parties.length === 1) {
        const party = data.staticData.partys[String(parties[0])];
        if (party) {
          response.party = party;
        }
      }
    }
    if (qp.wb) {
      const wb = qp.wb.split(',').map(Number).filter(Boolean);
      response.filters.wb = wb;
      fq.push(`org_id:(${wb.join(' OR ')})`);
    }
    // from_date = request.GET.get('from')
    // to_date = request.GET.get('to')
    // is_dz = request.GET.get('dz')
    // is_council = request.GET.get('council')
    // time_filter = request.GET.get('time_filter')
  }
  return [response, fq];
}

function search({ type, facet = false, highlight = false }) {
  return async (req, res) => {
    const query = req.query.q || '';
    const q = fixQuery(query);
    const startPage = Number(req.query.page) || 0;

    const [response, fq] = getFilters(type, req.query);
    fq.push(`type:${type}`);

    const solrJson = await solrSelect({
      highlight: query ? highlight : false, // don't hl if no query since we match everything
      facet,
    }, {
      fq: fq.join(' AND '),
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
      query,
      ...response,
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

function landing(req, res) {
  res.json({
    ok: true,
  });
}

module.exports = {
  landing,
  searchSpeeches: wrap(search({ type: 'speech', highlight: true, facet: true })),
  searchVotes: wrap(search({ type: 'vote', highlight: true })),
  searchLegislation: wrap(search({ type: 'legislation', highlight: true })),
  refetchData,
};
