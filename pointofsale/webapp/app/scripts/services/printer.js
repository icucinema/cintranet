'use strict';

/**
 * @ngdoc service
 * @name webappApp.printer
 * @description
 * # printer
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('printer', function ($http, busy) {
    this.list = function() {
      return busy.busy($http
        .get('/api/printers/')
        .then(function(res) {
          return res.data.results;
        }));
    };

    this.openDrawer = function(printer) {
      return busy.busy($http
        .post('/api/printers/' + printer.id + '/open_cash_drawer/'));
    };

    this.printTicket = function(printer, ticket) {
      return this.printTickets([ticket]);
    };

    this.printTickets = function(printer, tickets) {
      var data = {
        tickets: tickets.map(function(y) { return y.id }),
      };

      return busy.busy($http
        .post('/api/printers/' + printer.id + '/print_tickets/', data)
        .then(function(res) {
          return res.data;
        }));
    };

    this.printHead = function(printer, heading) {
      var data = {
        heading: heading,
      };

      return busy.busy($http
        .post('/api/printers/' + printer.id + '/print_head/', data)
        .then(function(res) {
          return res.data;
        }));
    };
  });
