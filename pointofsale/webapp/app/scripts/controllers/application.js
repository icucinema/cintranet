'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:ApplicationCtrl
 * @description
 * # ApplicationCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('ApplicationCtrl', function ($scope, AUTH_EVENTS, event, $interval) {
    $scope.currentUser = null;
    $scope.configuration = null;
    $scope.currentPunter = null;
    $scope.isLoading = false;

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

    var refreshing;
    var stopRefreshing = function() {
      if (angular.isDefined(refreshing)) {
        $interval.cancel(refreshing);
        refreshing = undefined;
      }
    };
    var doRefresh = function() {
      if (!angular.isDefined($scope.configuration) || $scope.configuration === null || !angular.isDefined($scope.configuration.events) || $scope.configuration.events === null || $scope.configuration.events.length === 0) {
        return;
      }

      var oevs = $scope.configuration.events;
      event.refresh($scope.configuration.events).then(function(results) {
        if ($scope.configuration.events !== oevs) return; // something's different
        $scope.configuration.events = results;
      });
    };
    refreshing = $interval(doRefresh, 5000);
    $scope.$on('$destroy', function() {
      stopRefreshing();
    });
  });
