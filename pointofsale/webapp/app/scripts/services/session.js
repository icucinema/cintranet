'use strict';

/**
 * @ngdoc service
 * @name webappApp.session
 * @description
 * # session
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('session', function () {
    // AngularJS will instantiate a singleton by calling "new" on this function
    var currentUser = {
      loggedIn: false,
      username: null,
      authToken: null,
    };

    this.create = function(username, authToken) {
      currentUser.username = username;
      currentUser.authToken = authToken;
      currentUser.loggedIn = true;
    };

    this.destroy = function() {
      currentUser.username = null;
      currentUser.authToken = null;
      currentUser.loggedIn = false;
    };

    this.getCurrentUser = function() {
      return currentUser;
    };
  });
