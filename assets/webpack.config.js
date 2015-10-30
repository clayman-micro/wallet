/* eslint no-var: 0 no-process-env: 0 */

var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var NODE_ENV = process.env.NODE_ENV;

var config = {
    entry: {
        vendor: ['react', 'react-dom', 'react-mixin',
                 'react-router', 'react-redux', 'redux', 'redux-router', 'redux-thunk',
                 'history', 'key-mirror'],
        app: './src/js/index.js',
        index: './src/htdocs/index.html'
    },
    output: {
        path: path.join(__dirname, 'build'),
        filename: 'assets/[name].bundle.js',
        publicPath: '/build/'
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin('vendor', 'assets/vendor.bundle.js'),
        new ExtractTextPlugin('assets/[name].bundle.css', { allChunks: true }),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new webpack.DefinePlugin({
            DEBUG: NODE_ENV !== 'production',
            HOST: JSON.stringify('http://localhost:5000')
        })
        //new webpack.ProvidePlugin({
        //    fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch'
        //})
    ],
    resolve: {
        root: path.join(__dirname, 'src'),
        extension: ['', '.js', '.jsx', '.less']
    },
    module: {
        loaders: [{
            test: /\.less$/,
            loader: ExtractTextPlugin.extract('style-loader',
                'css-loader?sourceMap!autoprefixer?browsers=last 2 version!less-loader?sourceMap')
        }, {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
        }, {
            test: /\.(otf|eot|png|svg|ttf|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            loader: 'url-loader?limit=8192'
        }, {
            test: /\.html$/,
            loader: 'file?name=[name].[ext]'
        }, {
            test: /\.js$/,
            loaders: ['babel-loader'],
            exclude: /node_modules/
        }]
    }
};

if (typeof process.env.NODE_ENV !== 'undefined' && process.env.NODE_ENV === 'production') {
    // Production config
    config.bail = true;
    config.debug = false;
    config.profile = false;
    config.devtool = '#source-map';

    config.output = {
        path: './build',
        pathInfo: true,
        publicPath: '/build/',
        filename: 'assets/[name].bundle.js'
    };

    config.plugins = config.plugins.concat([
        new webpack.optimize.OccurenceOrderPlugin(true),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.UglifyJsPlugin({ output: { comments: false } })
    ]);
} else {
    // Development config
    config.devtool = '#inline-source-map';
}

module.exports = config;
