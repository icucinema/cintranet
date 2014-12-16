'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:ApplicationCtrl
 * @description
 * # ApplicationCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('ApplicationCtrl', function ($scope, AUTH_EVENTS, events, $interval) {
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

    var refreshing;
    var stopRefreshing = function() {
      if (angular.isDefined(refreshing)) {
        $interval.cancel(refreshing);
        refreshing = undefined;
      }
    };
    var doRefresh = function() {
      if (!angular.isDefined($scope.configuration) || !angular.isDefined($scope.configuration.events)) {
        return;
      }

      var oevs = $scope.configuration.events;
      events.refresh($scope.configuration.events).then(function(results) {
        if ($scope.configuration.events !== oev) return; // something's different
        $scope.configuration.events = results;
      });
    };
    refreshing = $interval(doRefresh, 5000);
    $scope.$on('$destroy', function() {
      stopRefreshing();
    });
  });
