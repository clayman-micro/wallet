/* eslint no-var: 0 */

var webpack = require('webpack');
var config = require('./webpack.base.config.js');


var SaveAssetsJSON = require('assets-webpack-plugin');

config.bail = true;
config.debug = false;
config.profile = false;
config.devtool = '#source-map';

config.output = {
    path: './dist',
    pathInfo: true,
    publicPath: '/dist/',
    filename: 'bundle.[hash].min.js'
};

config.plugins = config.plugins.concat([
    new webpack.optimize.OccurenceOrderPlugin(true),
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.UglifyJsPlugin({ output: { comments: false } })
]);

config.module.loaders = config.module.loaders.concat([
    { test: /\.js$/, loaders: ['babel-loader'], exclude: /node_modules/ }
]);

module.exports = config;
