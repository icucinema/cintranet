'use strict';

/**
 * @ngdoc service
 * @name webappApp.ticket
 * @description
 * # ticket
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('ticket', function ($http, $q, printer) {
    var that = this;

    this.generate = function(specs, printerObj) {
      var submit = {
        tickets: specs,
        printerObj: printerObj.id,
      };

      return $http
        .post('/api/tickets/generate/?open_cashdrawer=true', submit)
        .then(function(res) {
          return res.data;
        });
    };

    this.collect = function(ticket) {
      return $http
        .post('/api/tickets/' + ticket.id + '/collect/')
        .then(function(res) {
          return res.data;
        })
    };

    this.collectAndPrint = function(ticket, printerObj) {
      if (ticket.length !== undefined && ticket.map) {
        return $q.all(ticket.map(function(x) {
          return that.collect(x, printerObj);
        })).then(function(tickets) {
          return printer.printTickets(printerObj, tickets);
        });
      } else {
        return this.collect(ticket).then(function() {
          return printer.printTicket(printerObj, ticket);
        });
      }
    };
  });
