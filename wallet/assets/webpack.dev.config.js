/* eslint no-var: 0, no-process-env: 0 */

var config = require('./webpack.base.config.js');

if (process.env.NODE_ENV !== 'test') {
    config.entry = [
        'webpack-dev-server/client?http://localhost:3000',
        'webpack/hot/only-dev-server',
        config.entry
    ];
}

config.output.publicPath = 'http://localhost:3000/static/';

config.devtool = '#inline-source-map';

config.module.loaders = config.module.loaders.concat([
    { test: /\.js$/, loaders: ['react-hot', 'babel-loader'], exclude: /node_modules/ }
]);

config.proxy = {
    '*': 'http://localhost:8080'
};

module.exports = config;
