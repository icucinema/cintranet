'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:ApplicationCtrl
 * @description
 * # ApplicationCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('ApplicationCtrl', function ($scope, AUTH_EVENTS) {
    $scope.currentUser = null;
    $scope.configuration = null;
    $scope.currentPunter = null;

    $scope.setCurrentUser = function(user) {
      $scope.currentUser = user;
    };
    $scope.setConfiguration = function(configuration) {
      $scope.configuration = configuration;
      $scope.$broadcast('configuration-change');
    };
    $scope.setCurrentPunter = function(punter) {
      $scope.currentPunter = punter;
      $scope.$broadcast('punter-change');
    };

    $scope.keyPressed = function($event) {
      if ($event.target.tagName == "INPUT") return;
      $scope.$broadcast('take-focus');
    };
  });
