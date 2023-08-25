// Bundle of the javascript into one File
const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: './src/index.js', // the main entry point for your application
  output: {
    path: path.resolve(__dirname, './static/frontend'), // the output directory for your bundled files
    filename: '[name].js', // the name of the bundled file
  },
  module: {
    rules: [
      // define any loaders or rules for processing different types of files
      {
        test: /\.js$/, // the regex pattern to match against the filenames of the files to be processed
        exclude: /node_modules/, // any files to be excluded from processing
        use: {
          loader: 'babel-loader', // the loader to use for processing the files
        //   options: {
        //     presets: ['@babel/preset-env'], // any Babel presets to be used for transpiling the files
        //   },
        },
      },
    ],
  },
  optimization:{
    minimize: true,
  },
  // devtool: 'source-map',
  plugins: [
    new webpack.DefinePlugin({
         'process.env.NODE_ENV' : JSON.stringify('production')
    })
],

};
