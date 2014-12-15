'use strict';

/**
 * @ngdoc service
 * @name webappApp.printer
 * @description
 * # printer
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('printer', function ($http) {
    this.list = function() {
      return $http
        .get('/api/printers/')
        .then(function(res) {
          return res.data.results;
        });
    };

    this.openDrawer = function(printer) {
      return $http
        .post('/api/printers/' + printer.id + '/open_cash_drawer/');
    };

    this.printTicket = function(printer, ticket) {
      return this.printTickets([ticket]);
    };

    this.printTickets = function(printer, tickets) {
      var data = {
        tickets: tickets.map(function(y) { return y.id }),
      };

      return $http
        .post('/api/printers/' + printer.id + '/print_tickets/', data)
        .then(function(res) {
          return res.data;
        });
    }
  });
