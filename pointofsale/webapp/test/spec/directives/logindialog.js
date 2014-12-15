'use strict';

describe('Directive: loginDialog', function () {

  // load the directive's module
  beforeEach(module('webappApp', 'app/views/logindialog.html'));

  var element,
    scope,
    template,
    AUTH_EVENTS;

  beforeEach(inject(function ($templateCache, $rootScope, _AUTH_EVENTS_) {
    scope = $rootScope.$new();
    AUTH_EVENTS = _AUTH_EVENTS_;

    template = $templateCache.get('app/views/logindialog.html');
    $templateCache.put('/views/logindialog.html', template);
  }));

  element = null; // placeholder

  // it('shouldn\'t error', inject(function ($compile) {
  //   element = angular.element('<login-dialog></login-dialog>');
  //   element = $compile(element)(scope);

  //   scope.$digest();
  //   scope.$emit(AUTH_EVENTS.loginRequired);
  // }));
});
