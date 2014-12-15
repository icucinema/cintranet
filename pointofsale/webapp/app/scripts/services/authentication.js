'use strict';

/**
 * @ngdoc service
 * @name webappApp.authentication
 * @description
 * # authentication
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('authentication', function ($http, session) {
    this.login = function(username, password) {
      /*jshint camelcase: false */
      return $http
        .post('/api/api-token-auth/', { username: username, password: password })
        .then(function(res) {
          session.create(username, res.data.token);
        });
    };

    this.logout = function() {
      session.destroy();
    };
  });
