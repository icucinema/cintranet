'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:SetupCtrl
 * @description
 * # SetupCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('SetupCtrl', function ($location, $scope, event, printer, AUTH_EVENTS) {
    var reload = function() {
      updateEvents($scope.eventDate);
      printer.list(null).then(function(res) {
        $scope.printers = res;
      });
    };
    var updateEvents = $scope.updateEvents = function(date) {
      $scope.eventsLoading = true;
      event.list(date).then(function(res) {
        $scope.eventsLoading = false;
        $scope.events = res;
      }, function() {
        $scope.eventsLoading = false;
      });
    };

    $scope.eventDate = new Date();

    $scope.events = [];
    var selectedEvents = $scope.selectedEvents = [];
    $scope.printers = [];

    $scope.addEvent = function(event) {
      if (selectedEvents.indexOf(event) !== -1) return;
      selectedEvents.push(event);
      event.selected = true;
    };
    $scope.removeEvent = function(event) {
      if (selectedEvents.indexOf(event) === -1) return;
      selectedEvents.splice(selectedEvents.indexOf(event), 1);
      event.selected = false;
    };

    $scope.doneConfiguring = function(selectedEvents, selectedPrinter) {
      if (!selectedEvents || selectedEvents.length == 0) return;
      if (!selectedPrinter || !$scope.printers) return;

      var actualPrinter = null;
      for (var i = 0; i < $scope.printers.length; i++) {
        if ($scope.printers[i].id == selectedPrinter) {
          actualPrinter = $scope.printers[i];
        }
      }
      if (!actualPrinter) return;

      $scope.setConfiguration({
        events: selectedEvents,
        printer: actualPrinter,
      });
      $location.url('/main');
    };

    reload();
    $scope.$on(AUTH_EVENTS.loginSuccess, reload);
  });
