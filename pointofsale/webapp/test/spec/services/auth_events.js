'use strict';

describe('Service: AUTH_EVENTS', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var AUTH_EVENTS;
  beforeEach(inject(function (_AUTH_EVENTS_) {
    AUTH_EVENTS = _AUTH_EVENTS_;
  }));

  it('should have a loginRequired property', function () {
    expect(AUTH_EVENTS.loginRequired).toBe('auth-login-required');
  });

  it('should have a loginSuccess property', function () {
    expect(AUTH_EVENTS.loginSuccess).toBe('auth-login-success');
  });

  it('should have a loginFailed property', function () {
    expect(AUTH_EVENTS.loginFailed).toBe('auth-login-failed');
  });

});
