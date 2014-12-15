'use strict';

/**
 * @ngdoc directive
 * @name webappApp.directive:myFocus
 * @description
 * # myFocus
 */
angular.module('webappApp')
  .directive('myFocus', function ($timeout) {
    return {
      restrict: 'A',
      link: function postLink(scope, element, attrs) {
        $timeout(function() {
          element[0].focus();
        }, 300);

        scope.$on('take-focus', function() {
          element[0].focus();
        });
      }
    };
  });
