// Rollup configuration for MARBEFES BBT Database
// Bundles all JavaScript modules into a single optimized file

import { nodeResolve } from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';

const isProduction = process.env.NODE_ENV === 'production';

export default {
  input: 'static/js/bundle-entry.js',

  output: {
    file: 'static/dist/app.bundle.js',
    format: 'iife', // Immediately Invoked Function Expression for browser
    name: 'MarbefesApp',
    sourcemap: !isProduction, // Source maps for development only
    banner: '/* MARBEFES BBT Database - Generated Bundle v1.2.4 */\n/* DO NOT EDIT - Edit source files in static/js/ instead */'
  },

  plugins: [
    nodeResolve(), // Resolve module imports

    // Minify in production mode only
    isProduction && terser({
      compress: {
        drop_console: false, // Keep console.log for now (we have debug system)
        drop_debugger: true,
        pure_funcs: ['debug.log'], // Remove debug.log calls in production
      },
      format: {
        comments: false, // Remove comments
        preamble: '/* MARBEFES BBT Database v1.2.4 */'
      }
    })
  ].filter(Boolean) // Remove falsy plugins
};
