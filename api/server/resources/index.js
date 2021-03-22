/* eslint-disable global-require */
module.exports = (app) => {
  app.get(['/', '/hello'], (req, res) => {
    res.json({
      ok: true,
    });
  });

  require('./search/routes')(app);
};
