/* eslint no-var: 0 no-process-env: 0 */

var path = require('path');
var express = require('express');
var webpack = require('webpack');
var config = require('./webpack.config');
var WEBPACK_HOST = process.env.WEBPACK_HOST;

if (typeof WEBPACK_HOST === 'undefined') {
    WEBPACK_HOST = 'localhost';
}

config.entry.app = [
    'webpack-hot-middleware/client?http://' + WEBPACK_HOST + ':3000',
    config.entry.app
];

config.output.publicPath = 'http://' + WEBPACK_HOST + ':3000/';


var app = express();
var compiler = webpack(config);

app.use(require('webpack-dev-middleware')(compiler, {
    noInfo: true,
    publicPath: config.output.publicPath
}));

app.use(require('webpack-hot-middleware')(compiler));

app.get('*', function(req, res) {
    res.sendFile(path.join(__dirname, 'src', 'htdocs', 'index.html'));
});

app.listen(3000, WEBPACK_HOST, function(err) {
    if (err) {
        console.log(err);
        return;
    }

    console.log('Listening at http://' + WEBPACK_HOST + ':3000');
});
