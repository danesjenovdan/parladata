const controller = require('./controller');

module.exports = (app) => {
  app.get('/v2/search', controller.search);

  app.get('/api/data/refetch', controller.refetchData);
};
