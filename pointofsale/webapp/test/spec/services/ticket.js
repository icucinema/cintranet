'use strict';

describe('Service: ticket', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var ticket;
  beforeEach(inject(function (_ticket_) {
    ticket = _ticket_;
  }));

  it('should do something', function () {
    expect(!!ticket).toBe(true);
  });

});
