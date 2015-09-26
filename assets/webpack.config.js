/* eslint no-var: 0 no-process-env: 0 */

var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var NODE_ENV = process.env.NODE_ENV;

var config = {
    entry: {
        vendor: ['react', 'react-dom', 'react-mixin',
                 'react-router', 'react-redux', 'redux', 'redux-router', 'redux-thunk',
                 'redux-devtools', 'history', 'key-mirror'],
        app: './src/js/index.js',
        test: './src/js/test.js',
        index: './src/htdocs/index.html'
    },
    output: {
        path: path.join(__dirname, '..', 'build'),
        filename: '[name].bundle.js',
        publicPath: '/build/'
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js'),
        new ExtractTextPlugin('bundle.css', { allChunks: true }),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify(NODE_ENV)
        }),
        new webpack.ProvidePlugin({
            fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch'
        })
    ],
    resolve: {
        root: path.join(__dirname, 'src'),
        extension: ['', '.js', '.jsx', '.less']
    },
    module: {
        loaders: [{
            test: /\.less$/,
            loader: ExtractTextPlugin.extract('style-loader', 'css-loader?sourceMap!autoprefixer?browsers=last 2 version!less-loader?sourceMap')
        }, {
            test: /\.css$/,
            loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
        }, {
            test: /\.(otf|eot|png|svg|ttf|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            loader: 'url-loader?limit=8192'
        }, {
            test: /\.html$/,
            loader: 'file?name=[name].[ext]'
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
        filename: '[name].bundle.js'
    };

    config.plugins = config.plugins.concat([
        new webpack.optimize.OccurenceOrderPlugin(true),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.UglifyJsPlugin({ output: { comments: false } })
    ]);

    config.module.loaders = config.module.loaders.concat([
        { test: /\.js$/, loaders: ['babel-loader'], exclude: /node_modules/ }
    ]);
} else {
    // Development config
    config.devtool = '#inline-source-map';

    config.module.loaders = config.module.loaders.concat([
        { test: /\.js$/, loaders: ['react-hot', 'babel-loader'], exclude: /node_modules/ }
    ]);
}

module.exports = config;
