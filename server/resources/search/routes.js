const controller = require('./controller');

module.exports = (app) => {
  app.get('/', controller.landing);

  app.get('/search/speeches', controller.searchSpeeches);
  app.get('/search/votes', controller.searchVotes);
  app.get('/search/legislation', controller.searchLegislation);

  app.get('/api/data/refetch', controller.refetchData);
};
