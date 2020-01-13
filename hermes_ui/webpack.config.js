let webpack = require('webpack');
let config = require('./assets/config');
let ManifestPlugin = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
let OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
let path = require('path');

module.exports = {
    context: path.join(__dirname, config.build.context),
    entry: {
        app: "./scripts/app.js",
        app_help: './scripts/app_help.js',
        app_hermes: './scripts/app_hermes.js'
    },
    output: {
        path: path.join(__dirname, config.build.assetsPath),
        filename: 'js/[name].[chunkhash].js',
        publicPath: path.join(__dirname, config.build.assetsURL)
    },
    optimization: {
        minimizer: [new TerserPlugin()],
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: '../',
                            hmr: process.env.NODE_ENV === 'development',
                        },
                    },
                    //'style-loader',
                    'css-loader'
                ],
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            {
                test: /\.(woff2?|eot|ttf|otf|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                    name: 'fonts/[name].[hash:7].[ext]',
                    publicPath: '../build/',
                }
            },
            {
                test: /\.(png|jpg|gif)$/i,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 8192,
                        },
                    },
                ],
            },
        ]
    },
    plugins: [
        new ManifestPlugin({
            fileName: 'manifest.json',
            stripSrc: true,
            publicPath: config.build.assetsURL
        }),
        new MiniCssExtractPlugin(
            {
                // Options similar to the same options in webpackOptions.output
                // all options are optional
                filename: '[name].css',
                chunkFilename: '[id].css',
                ignoreOrder: false, // Enable to remove warnings about conflicting order

            }
        ),
        new OptimizeCssAssetsPlugin({
            assetNameRegExp: /\.css$/g,
            cssProcessor: require('cssnano'),
            cssProcessorPluginOptions: {
                preset: ['default', {discardComments: {removeAll: true}}],
            },
            canPrint: true
        }),
        // new webpack.ProvidePlugin({
        //     jQuery: 'jquery/src/jquery',
        //     $: 'jquery/src/jquery',
        //     jquery: 'jquery/src/jquery',
        //     'window.jQuery': 'jquery/src/jquery'
        // })
    ]
};