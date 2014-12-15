'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:LoginCtrl
 * @description
 * # LoginCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('LoginCtrl', function ($scope, $rootScope, authentication, AUTH_EVENTS) {
    $scope.credentials = {
      username: '',
      password: '',
    };

    $scope.login = function(credentials) {
      authentication.login(credentials.username, credentials.password).then(function() {
        $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
        $scope.setCurrentUser(credentials.username);
      }, function() {
        $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
        $scope.setCurrentUser(null);
      });
    };
  });
