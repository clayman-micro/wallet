/* eslint no-var: 0, no-console: 0 */

var webpack = require('webpack');
var WebpackDevServer = require('webpack-dev-server');
var config = require('./webpack.config');

config.entry.app = [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/only-dev-server',
    config.entry.app
];

config.output.publicPath = 'http://localhost:3000/';


new WebpackDevServer(webpack(config), {
    publicPath: config.output.publicPath,
    hot: true,
    historyApiFallback: true
}).listen(3000, 'localhost', function (err, result) {
    if (err) {
        console.log(err);
    }

    console.log('Listening at localhost:3000');
});
