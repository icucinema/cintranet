'use strict';

describe('Service: session', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var session;
  beforeEach(inject(function (_session_) {
    session = _session_;
  }));

  it('should have a currentUser', function () {
    expect(session.getCurrentUser).toBeDefined();
  });
  it('should set currentUser on create', function () {
    session.create('aardvark', 'fffff');
    var user = session.getCurrentUser();
    expect(user.username).toBe('aardvark');
    expect(user.authToken).toBe('fffff');
  });
  it('should nuke currentUser on destroy', function() {
    var user = session.getCurrentUser();
    session.create('aardvark', 'fffff');
    expect(user.username).toBe('aardvark');
    expect(user.authToken).toBe('fffff');
    session.destroy();
    expect(user.username).toBe(null);
    expect(user.authToken).toBe(null);
  });

});
