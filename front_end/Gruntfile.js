// Load Grunt
module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Tasks
    sass: {
      // Begin Sass Plugin
      dist: {
        options: {
          sourcemap: 'none',
        },
        files: [
          {
            expand: true,
            cwd: 'scss',
            src: ['**/*.scss'],
            dest: 'hidentostatic/hidentocss',
            ext: '.css',
          },
        ],
      },
    },
    postcss: {
      // Begin Post CSS Plugin
      options: {
        map: false,
        processors: [
          require('autoprefixer')(),
        ],
      },
      dist: {
        src: ['hidentostatic/hidentocss/hidentostyle.css', 'hidentostatic/hidentocss/appstyle.css'],
      },
    },
    cssmin: {
      // Begin CSS Minify Plugin
      target: {
        files: [
          {
            expand: true,
            cwd: '.',
            src: ['hidentostatic/hidentocss/hidentostyle.css', 'hidentostatic/hidentocss/appstyle.css'],
            dest: '.',
            ext: '.min.css',
          },
        ],
      },
    },
    uglify: {
      // Begin JS Uglify Plugin
      build: {
        src: ['hidentostatic/hidentojs/hidentoscript.js'],
        dest: 'hidentostatic/hidentojs/hidentoscript.min.js',
      },
    },
    watch: {
      // Compile everything into one task with Watch Plugin
      css: {
        files: 'scss/*.scss',
        tasks: ['sass', 'postcss', 'cssmin'],
      },
      js: {
        files: 'hidentostatic/hidentojs/hidentoscript.js',
        tasks: ['uglify'],
      },
    },
  })
  // Load Grunt plugins
  grunt.loadNpmTasks('grunt-contrib-sass')
  grunt.loadNpmTasks('grunt-postcss')
  grunt.loadNpmTasks('grunt-contrib-cssmin')
  grunt.loadNpmTasks('grunt-contrib-uglify')
  grunt.loadNpmTasks('grunt-contrib-watch')

  // Register Grunt tasks
  grunt.registerTask('default', ['watch'])
}