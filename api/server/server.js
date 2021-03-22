const express = require('express');
const chalk = require('chalk');
const bodyParser = require('body-parser');
const cors = require('cors');
const config = require('../config');

const app = express();

function setupExpress() {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-console
    console.log(`${chalk.magenta('| EXPRESS SERVER |')} - ${chalk.green('starting')}`);

    // disable "X-Powered-By: Express" header
    app.disable('x-powered-by');

    app.use(cors());
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true }));

    // eslint-disable-next-line global-require
    require('./resources')(app);

    app.get('*', (req, res) => {
      res.status(404).json({
        error: true,
        status: 404,
        message: 'Not Found',
      });
    });

    // start listening on port
    const server = app.listen(config.port, () => {
      // eslint-disable-next-line no-console
      console.log(`${chalk.magenta('| EXPRESS SERVER |')} - ${chalk.green(`started on: http://localhost:${config.port}/`)}`);
      resolve();
    });

    server.on('error', (err) => {
      reject(err);
    });

    server.timeout = config.serverTimeout;
  });
}

function init() {
  return Promise.resolve()
    .then(setupExpress);
}

module.exports = {
  init,
};
