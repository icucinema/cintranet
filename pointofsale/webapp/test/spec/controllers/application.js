'use strict';

describe('Controller: ApplicationCtrl', function () {

  // load the controller's module
  beforeEach(module('webappApp'));

  var ApplicationCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    ApplicationCtrl = $controller('ApplicationCtrl', {
      $scope: scope
    });
  }));

  it('should have a currentUser', function () {
    expect(scope.currentUser).toBeDefined();
  });
  it('should have setCurrentUser', function () {
    expect(scope.setCurrentUser).toBeDefined();
  });
  it('should set currentUser when setCurrentUser is called', function () {
    expect(scope.currentUser).toBe(null);
    scope.setCurrentUser('aardvark');
    expect(scope.currentUser).toBe('aardvark');
  });
});
