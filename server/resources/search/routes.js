const controller = require('./controller');

module.exports = (app) => {
  app.get('/', controller.landing);

  app.get('/search/speeches', controller.searchSpeeches);
  app.get('/search/votes', controller.searchVotes);
  app.get('/search/legislation', controller.searchLegislation);

  app.get('/tfidf/person', controller.tfidfPerson);
  app.get('/tfidf/party', controller.tfidfParty);
  app.get('/tfidf/session', controller.tfidfSession);

  app.get('/api/data/refetch', controller.refetchData);
};
