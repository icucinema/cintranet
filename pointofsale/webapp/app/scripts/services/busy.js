'use strict';

/**
 * @ngdoc service
 * @name webappApp.busy
 * @description
 * # busy
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('busy', function ($rootScope) {
    var busyCount = 0;

    var setBusy = function() {
      $rootScope.isBusy = busyCount > 0;
    };

    var pushBusy = function() {
      busyCount++;
      setBusy();
    };
    var popBusy = function() {
      busyCount--;
      setBusy();
    };

    this.busy = function(q) {
      pushBusy();
      return q.finally(function() {
        popBusy();
      });
    };
  });
