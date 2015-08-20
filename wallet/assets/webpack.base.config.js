/* eslint no-var: 0, no-process-env: 0 */

var path = require('path');
var webpack = require('webpack');
var objectAssign = require('object-assign');

var NODE_ENV = process.env.NODE_ENV;

var env = {
    production: NODE_ENV === 'production',
    development: NODE_ENV === 'development' || typeof NODE_ENV === 'undefined'
};

objectAssign(env, {
    build: env.production
});

module.exports = {
    entry: './src/js/app.js',
    output: {
        path: path.join(__dirname, 'dist'),
        filename: 'bundle.js',
        publicPath: '/static/'
    },
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoErrorsPlugin(),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify(NODE_ENV)
        }),
        new webpack.ProvidePlugin({
            'fetch': 'imports?this=>global!exports?global.fetch!whatwg-fetch'
        })
    ],
    resolve: {
        extension: ['', '.js', '.jsx', '.less']
    },
    module: {
        loaders: [{
            test: /\.less$/,
            loader: 'style!css!autoprefixer?browsers=last 2 version!less'
        }]
    }
};