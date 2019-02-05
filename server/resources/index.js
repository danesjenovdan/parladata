/* eslint-disable global-require */
module.exports = (app) => {
  require('./search/routes')(app);
};
