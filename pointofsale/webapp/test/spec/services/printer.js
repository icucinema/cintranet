'use strict';

describe('Service: printer', function () {

  // load the service's module
  beforeEach(module('webappApp'));

  // instantiate service
  var printer;
  beforeEach(inject(function (_printer_) {
    printer = _printer_;
  }));

  it('should do something', function () {
    expect(!!printer).toBe(true);
  });

});
