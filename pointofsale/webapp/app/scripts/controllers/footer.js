'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:FooterCtrl
 * @description
 * # FooterCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('FooterCtrl', function ($scope, punter, ticket, printer) {
    $scope.currentPunterName = function() {
      if (!$scope.currentPunter) return 'Guest';
      if (!$scope.currentPunter.name || !$scope.currentPunter.name.trim()) return '(Unknown: ID: ' + $scope.currentPunter.id + ')';
      return $scope.currentPunter.name;
    };

    var checkPunterHasPendingTickets = function(punterObj) {
      punter.getPendingTickets(punterObj).then(function(res) {
        if (res.length > 0) {
          printer.printHead($scope.configuration.printer, punterObj.name).then(function(x) {
            return ticket.collectAndPrint(res, $scope.configuration.printer);
          }, function(x) {
            alert('Couldn\'t print their name?!?');
          }).then(function(x) {
            alert('Printed ' + x.count + ' tickets for collection');
          }, function(x) {
            alert('Failed to print tickets for collection - some tickets may have gone AWOL!');
          });
        } else {
          $scope.setCurrentPunter(punterObj);
        }
      }, function() {
        console.log('Call to check pending failed?!?');
        $scope.setCurrentPunter(punterObj);
      });
    };

    $scope.searchAndSelectPunter = function(search) {
      $scope.searchDisabled = true;
      punter.search(search).then(function(res) {
        $scope.searchDisabled = false;
        $scope.search = '';
        if (res.length == 0) {
          $scope.setCurrentPunter(null);
        } else if (res.length == 1) {
          checkPunterHasPendingTickets(res[0]);
        } else {
          checkPunterHasPendingTickets(res[0]);
        }
      }, function() {
        $scope.searchDisabled = false;
        $scope.search = '';
      });
    };
  });
