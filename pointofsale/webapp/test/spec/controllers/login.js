'use strict';

describe('Controller: LoginCtrl', function () {

  // load the controller's module
  beforeEach(module('webappApp'));

  var LoginCtrl,
    authentication,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    authentication = {
      login: function() {},
    };
    LoginCtrl = $controller('LoginCtrl', {
      $scope: scope,
      authentication: authentication,
    });
  }));

  it('should attach a login method to the scope', function() {
    expect(scope.login).toBeDefined();
  });
  it('should invoke authentication when login is called', function() {
    spyOn(authentication, 'login').and.returnValue({ then: function(){} });
    scope.login({ username: 'aardvark', password: 'guest' });
    expect(authentication.login).toHaveBeenCalledWith('aardvark', 'guest');
  });
  it('should broadcast success on login success', function() {
    var test = {
      worked: function(){},
    };

    scope.setCurrentUser = function() {};
    scope.$on('auth-login-success', function() {
      test.worked();
    });

    spyOn(scope, 'setCurrentUser');
    spyOn(authentication, 'login').and.returnValue({ then: function(ok){ ok(); } });
    spyOn(test, 'worked');

    scope.login({ username: 'aardvark', password: 'guest' });

    expect(scope.setCurrentUser).toHaveBeenCalledWith('aardvark');
    expect(test.worked).toHaveBeenCalled();
  });
  it('should broadcast failure on login failure', function() {
    var test = {
      worked: function(){},
    };

    scope.setCurrentUser = function() {};
    scope.$on('auth-login-failed', function() {
      test.worked();
    });

    spyOn(scope, 'setCurrentUser');
    spyOn(authentication, 'login').and.returnValue({ then: function(ok, fail){ fail(); } });
    spyOn(test, 'worked');

    scope.login({ username: 'aardvark', password: 'guest' });

    expect(scope.setCurrentUser).toHaveBeenCalledWith(null);
    expect(test.worked).toHaveBeenCalled();
  });
});
