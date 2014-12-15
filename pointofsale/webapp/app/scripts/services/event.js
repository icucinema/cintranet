'use strict';

/**
 * @ngdoc service
 * @name webappApp.event
 * @description
 * # event
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('event', function ($http) {
    this.list = function(date) {
      return $http
        .get(
          '/api/events/',
          {
            params: { date: date }
          })
        .then(function(resp) {
          return resp.data.results;
        });
    };

    this.getById = function(id) {
      return $http
        .get('/api/events/' + id + '/')
        .then(function(resp) {
          return resp.data;
        });
    };
  });
