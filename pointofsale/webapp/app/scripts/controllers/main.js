'use strict';

/**
 * @ngdoc function
 * @name webappApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the webappApp
 */
angular.module('webappApp')
  .controller('MainCtrl', function ($scope, $location, ticketType, printer, ticket) {
    if ($scope.configuration == null) {
      $location.url('/setup');
    }

    $scope.currentEvent = $scope.configuration.events[0];
    $scope.tickets = [];
    $scope.cart = [];

    $scope.selectTicket = function(ticket) {
      $scope.cart.push(ticket);
    };
    $scope.removeTicket = function(id) {
      $scope.cart.splice(id, 1);
    }
    $scope.clearCart = function() {
      $scope.cart = [];
    };
    $scope.totalCartValue = function(cart) {
      var currentValue = 0;
      cart.forEach(function(item) {
        currentValue += item.sale_price * 100;
      });
      return currentValue / 100;
    };

    $scope.noSale = function(cart) {
      if (!cart || !cart.length) {
        // open the cash drawer
        printer.openDrawer($scope.configuration.printer);
      }
      $scope.clearCart();
      $scope.setCurrentPunter(null);
    };
    $scope.checkout = function(cart) {
      if (!cart || !cart.length) return;
      // make some specs
      var punterId = $scope.currentPunter ? $scope.currentPunter.id : null;

      var specs = cart.map(function(x) {
        return {
          ticket_type: x.id,
          punter: punterId,
        }
      });

      ticket.generate(specs, $scope.configuration.printer).then(function(res) {
        $scope.clearCart();
        $scope.setCurrentPunter(null);
      })
    };

    var refreshAllTickets = function() {
      $scope.clearCart();
      return ticketType.refresh($scope.currentPunter, $scope.configuration.events).then(function() {
        refreshTickets();
      });
    };
    var refreshTickets = function() {
      ticketType.forEvent($scope.currentEvent).then(function(tickets) {
        $scope.tickets = tickets;
      });
    };
    $scope.selectEvent = function(event) {
      $scope.currentEvent = event;
      refreshTickets();
    };
    $scope.$on('punter-change', refreshAllTickets);
    $scope.$on('configuration-change', refreshAllTickets);
    $scope.currentEvent = $scope.configuration.events[0];
    refreshAllTickets();
  });
