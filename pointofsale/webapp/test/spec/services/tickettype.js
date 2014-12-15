'use strict';

describe('Service: ticketTypes', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var ticketTypes;
  beforeEach(inject(function (_ticketTypes_) {
    ticketTypes = _ticketTypes_;
  }));

  it('should do something', function () {
    expect(!!ticketTypes).toBe(true);
  });

});
