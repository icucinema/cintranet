'use strict';

/**
 * @ngdoc service
 * @name webappApp.ticketType
 * @description
 * # ticketType
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('ticketType', function ($q, $http) {
    var internalCache = null;
    var defaultCache = null;
    var lastEvents = null;

    this.forEvent = function(event) {
      if (!internalCache) return $q.reject('must refresh');
      return $q(function(resolve, reject) {
        return resolve(internalCache[event.id]);
      });
    };

    this.refresh = function(punter, events) {
      return $q(function(resolve, reject) {
        var tmpCache = {};
        if (!punter) {
          if (defaultCache && lastEvents == events) {
            internalCache = defaultCache;
            return resolve();
          }

          // regenerate defaultCache
          var promisesDict = {};
          events.forEach(function(x) {
            promisesDict[x.id] = $http
              .get('/api/events/' + x.id + '/ticket_types/');
          });

          $q.all(promisesDict)
            .then(function(res) {
              for (var key in res) {
                if (!res.hasOwnProperty(key)) continue;
                tmpCache[key] = res[key].data;
              }
              internalCache = defaultCache = tmpCache;
              resolve();
            }, function(res) {
              reject(res);
            });
        } else {
          $http
            .get('/api/punters/' + punter.id + '/ticket_types/', {
              params: {
                sale_point: 'on_door',
                events: events.map(function(x) { return x.id }),
              }
            })
            .then(function(res) {
              for (var i = 0; i < res.data.length; i++) {
                var thisTicket = res.data[i];
                if (tmpCache[thisTicket.event] === undefined) {
                  tmpCache[thisTicket.event] = [];
                }
                tmpCache[thisTicket.event].push(thisTicket);
              }
              internalCache = tmpCache;
              return resolve();
            }, function(res) {
              return reject(res);
            });
        }
      });
    };
  });
