'use strict';

/**
 * @ngdoc service
 * @name webappApp.AUTH_EVENTS
 * @description
 * # AUTH_EVENTS
 * Constant in the webappApp.
 */
angular.module('webappApp')
  .constant('AUTH_EVENTS', {
    'loginSuccess': 'auth-login-success',
    'loginFailed': 'auth-login-failed',
    'loginRequired': 'auth-login-required'
  });
