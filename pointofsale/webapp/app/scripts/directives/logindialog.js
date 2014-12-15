'use strict';

/**
 * @ngdoc directive
 * @name webappApp.directive:loginDialog
 * @description
 * # loginDialog
 */
angular.module('webappApp')
  .directive('loginDialog', function (AUTH_EVENTS) {
    return {
      templateUrl: '/views/logindialog.html',
      replace: true,
      restrict: 'E',
      link: function postLink(scope, element) {
        var inited = false;

        var init = function() {
          element.modal({
            keyboard: false,
            backdrop: 'static',
            show: false,
          });
          inited = true;
        };

        scope.$on(AUTH_EVENTS.loginRequired, function() {
          if (!inited) {
            init();
          }
          element.modal('show');
        });
        scope.$on(AUTH_EVENTS.loginSuccess, function() {
          if (!inited) {
            init();
          }
          element.modal('hide');
        });
      }
    };
  });
