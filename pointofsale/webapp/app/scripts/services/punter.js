'use strict';

/**
 * @ngdoc service
 * @name webappApp.punter
 * @description
 * # punter
 * Service in the webappApp.
 */
angular.module('webappApp')
  .service('punter', function ($http, busy) {
    var currentPunter = null;

    this.getCurrentPunter = function() {
      return currentPunter;
    };

    this.search = function(searchTerm) {
      // lets try and work out whether this is a card ID or not...
      var isCard = false;
      if ((searchTerm.length % 2) == 0 && searchTerm.length >= 8) {
        // it's probably a card
        isCard = true;

        // unless it doesn't contain hex, in which case, nope
        for (var i = 0; i < searchTerm.length; i++) {
          var ch = searchTerm.charAt(i);
          if (isNaN(parseInt(ch, 16))) {
            isCard = false;
            break;
          }
        }

        // however, it might be a CID...
        if (isCard && searchTerm.length == 8 && searchTerm.charAt(0) == '0') {
          isCard = false;
          for (var i = 0; i < searchTerm.length; i++) {
            var ch = searchTerm.charAt(i);
            if (isNaN(parseInt(ch, 10))) {
              isCard = true;
              break;
            }
          }
        }
      } else if (searchTerm.charAt(0) == ';' && searchTerm.charAt(searchTerm.length-1) == '?') {
        // looks like a swipe card to me
        isCard = true;
      }

      var searchParams = {};
      if (isCard) {
        searchParams.card_id = searchTerm;
      } else {
        searchParams.search = searchTerm;
      }

      return busy.busy($http
        .get('/api/punters/', {
          params: searchParams,
        })
        .then(function(res) {
          return res.data.results;
        }));
    };

    this.getPendingTickets = function(punter) {
      return busy.busy($http
        .get('/api/punters/' + punter.id + '/tickets/?status=pending_collection')
        .then(function(res) {
          return res.data;
        }));
    };
  });
