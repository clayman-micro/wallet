/* eslint no-var: 0 vars-on-top: 0 */

var gulp = require('gulp');
var gutil = require('gulp-util');
var less = require('gulp-less');
var sourcemaps = require('gulp-sourcemaps');
var autoprefixer = require('gulp-autoprefixer');
var webpack = require('webpack');

var src = './src';
var dest = './build';
var path = require('path');
var config = {
    less: {
        src: src + '/styles/app.less',
        watch: src + '/styles/**/*.less',
        dest: dest + '/css',
        options: {
            paths: ['.', './components']
        }
    },
    markup: {
        src: src + '/**.html',
        watch: src + '/**.html',
        dest: dest
    },
    webpack: {
        devtool: '#inline-source-map',
        entry: {
            app: './src/js/app.js',
            vendors: ['jquery', 'react', 'react-router', 'flux']
        },
        output: {
            path: path.join(__dirname, dest, 'js'),
            filename: '[name].js',
            chunkFilename: '[chunkhash].js'
        },
        module: {
            loaders: [
                { test: /\.js$/, loader: 'babel-loader' }
            ]
        },
        plugins: [
            new webpack.optimize.CommonsChunkPlugin('vendors', 'vendors.js')
        ]
    }
};

gulp.task('less', function () {
    return gulp.src(config.less.src)
        .pipe(sourcemaps.init())
        .pipe(less(config.less.options))
        .pipe(sourcemaps.write())
        .pipe(autoprefixer({ browser: ['last 3 version'] }))
        .pipe(gulp.dest(config.less.dest));
});

gulp.task('markup', function () {
    return gulp.src(config.markup.src)
        .pipe(gulp.dest(config.markup.dest));
});

var webpackLog = function (name, err, stats) {
    if (err) {
        throw new gutil.PluginError(name, err);
    }
    gutil.log('[' + name + ']', stats.toString({
        colors: true
    }));
};

gulp.task('webpack:dev', function (callback) {
    var devConfig = Object.create(config.webpack);
    devConfig.debug = true;

    webpack(devConfig, function (err, stats) {
        webpackLog('webpack:dev', err, stats);
        callback();
    });
});

gulp.task('webpack:watch', function () {
    var watchConfig = Object.create(config.webpack);
    watchConfig.watch = true;

    webpack(watchConfig, function (err, stats) {
        webpackLog('webpack:watch', err, stats);
        gutil.log('[webpack:watch]', 'Waiting for changes...');
    });
});

gulp.task('webpack:build', function (callback) {
    var buildConfig = Object.create(config.webpack);
    buildConfig.plugins = buildConfig.plugins.concat(
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.UglifyJsPlugin()
    );

    webpack(buildConfig, function (err, stats) {
        webpackLog('webpack:build', err, stats);
        callback();
    });
});

gulp.task('default', ['markup', 'less', 'webpack:dev']);

gulp.task('watch', ['markup', 'less'], function () {
    gulp.watch(config.markup.watch, ['markup']);
    gulp.watch(config.less.watch, ['less']);
});

gulp.task('build', ['markup', 'less', 'webpack:build']);
