/* eslint no-var: 0 no-process-env: 0 */

var autoprefixer = require('autoprefixer');
var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var NODE_ENV = process.env.NODE_ENV;

var config = {
    entry: {
        app: './src/js/index.js'
    },
    output: {
        path: path.join(__dirname, 'build'),
        filename: '[name].bundle.js',
        publicPath: '/'
    },
    plugins: [
        // new webpack.optimize.CommonsChunkPlugin('vendor', 'vendor.bundle.js'),
        new ExtractTextPlugin('[name].bundle.css', { allChunks: true }),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new webpack.DefinePlugin({
            DEBUG: NODE_ENV !== 'production',
            TESTING: NODE_ENV === 'testing',
            HOST: JSON.stringify('http://localhost:5000')
        })
    ],
    resolve: {
        root: path.join(__dirname, 'src'),
        extension: ['', '.js', '.jsx', '.less']
    },
    module: {
        loaders: [{
            test: /\.less$/,
            loader: ExtractTextPlugin.extract('style-loader',
                'css-loader!postcss-loader!less-loader?sourceMap')
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
    },
    postcss: function () {
        return [autoprefixer({ browsers: ['last 2 versions'] })];
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
        publicPath: '/',
        filename: '[name].bundle.js'
    };

    config.plugins = config.plugins.concat([
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        }),
        new webpack.optimize.OccurenceOrderPlugin(true),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.UglifyJsPlugin({
            output: { comments: false },
            compress: { warnings: true }
        })
    ]);
} else {
    // Development config
    config.devtool = '#inline-source-map';
}

module.exports = config;
