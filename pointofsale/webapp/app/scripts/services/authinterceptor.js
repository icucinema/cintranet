'use strict';

/**
 * @ngdoc service
 * @name webappApp.authInterceptor
 * @description
 * # authInterceptor
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('authInterceptor', function ($rootScope, $q, session, AUTH_EVENTS) {
    this.responseError = function(response) {
      $rootScope.$broadcast({
        401: AUTH_EVENTS.loginRequired,
        403: AUTH_EVENTS.loginRequired,
      }[response.status], response);
      return $q.reject(response);
    };

    this.request = function(config) {
      var user = session.getCurrentUser();
      if (user.authToken) {
        config.headers.Authorization = 'Token ' + user.authToken;
      }
      return config;
    };
  });
