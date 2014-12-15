'use strict';

describe('Service: authentication', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // mock session
  var session;
  beforeEach(function() {
    session = {
      create: function() {}
    };
    spyOn(session, 'create');

    module(function($provide) {
      $provide.value('session', session);
    });
  });

  // instantiate service
  var authentication;
  var $httpBackend;
  beforeEach(inject(function (_authentication_, _$httpBackend_) {
    authentication = _authentication_;
    $httpBackend = _$httpBackend_;
  }));

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });

  it('should allow login', function () {
    $httpBackend.whenPOST('/api/api-token-auth/').respond(200, '{"token": "aaaa"}', function(data) {
      return data === '{"username": "test", "password": "test2"}';
    });

    authentication.login('test', 'test2').then(function() {
      expect(true).toBe(true);
    }, function() {
      expect(false).not.toBe(false);
    });

    $httpBackend.flush();

    expect(session.create).toHaveBeenCalled();
  });

});
