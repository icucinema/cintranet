'use strict';

describe('Service: punter', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var punter;
  beforeEach(inject(function (_punter_) {
    punter = _punter_;
  }));

  it('should do something', function () {
    expect(!!punter).toBe(true);
  });

});
