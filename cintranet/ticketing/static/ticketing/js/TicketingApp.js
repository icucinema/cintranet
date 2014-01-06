var STANDARD_EVENT_TYPE = 1;
var DOUBLEBILL_EVENT_TYPE = 2;

var app = angular.module('TicketingApp', [
	'ngRoute',
	'restangular'
]);

app.constant('djurl', __djurls);

app.config(['djurl', '$routeProvider', '$httpProvider', 'RestangularProvider', function(djurl, $routeProvider, $httpProvider, RestangularProvider) {
	RestangularProvider.setResponseExtractor(function(response, operation, what, url) {
		if (operation === "getList") {
			// Use results as the return type, and save the result metadata
			// in _resultmeta
			if (!response.results) return response;
			var newResponse = response.results;
			newResponse._resultmeta = {
				"count": response.count,
				"next": response.next,
				"previous": response.previous,
			};
			return newResponse;
		}
		
		return response;
	});
	RestangularProvider.setBaseUrl(djurl.api_root);
	RestangularProvider.setRequestSuffix('/');
	RestangularProvider.setRestangularFields({
		selfLink: 'url'
	});
	$routeProvider.
		when('/', {
			templateUrl: djurl.partial_root + 'index.html',
			controller: 'IndexCtrl'
		}).
		when('/events', {
			templateUrl: djurl.partial_root + 'events.html',
			controller: 'EventsCtrl'
		}).
		when('/events/:id', {
			templateUrl: djurl.partial_root + 'event.html',
			controller: 'EventCtrl'
		}).
		when('/showings', {
			templateUrl: djurl.partial_root + 'showings.html',
			controller: 'ShowingsCtrl'
		}).
		when('/showings/create', {
			templateUrl: djurl.partial_root + 'showingwizard.html',
			controller: 'ShowingWizardCtrl'
		}).
		when('/showings/:id', {
			templateUrl: djurl.partial_root + 'showing.html',
			controller: 'ShowingCtrl'
		}).
		when('/films', {
			templateUrl: djurl.partial_root + 'films.html',
			controller: 'FilmsCtrl'
		}).
		when('/films/:id', {
			templateUrl: djurl.partial_root + 'film.html',
			controller: 'FilmCtrl'
		}).
		when('/punters', {
			templateUrl: djurl.partial_root + 'punters.html',
			controller: 'PuntersCtrl'
		}).
		when('/punters/:id', {
			templateUrl: djurl.partial_root + 'punter.html',
			controller: 'PunterCtrl'
		}).
		otherwise({
			redirectTo: '/'
		});
	$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	$httpProvider.defaults.xsrfCookieName = 'csrftoken';
}]);

app.directive('ngConfirmClick', [
  function(){
    return {
      priority: -1,
      restrict: 'A',
      link: function(scope, element, attrs){
        element.bind('click', function(e){
          var message = attrs.ngConfirmClick;
          if(message && !confirm(message)){
            e.stopImmediatePropagation();
            e.preventDefault();
          }
        });
      }
    }
  }
]);
app.directive('tabs', function() {
	return {
		restrict: 'E',
		scope: {},
		transclude: true,
		template: '<section class="tabs"><ul class="tab-nav"><li ng-repeat="pane in panes" ng-class="{active: pane.active}"><a href ng-click="select(pane)">{{ pane.tabTitle }}</a></li></ul><div ng-transclude></div></section>',
		controller: function($scope) {
			var panes = $scope.panes = [];
			$scope.select = function(pane) {
				angular.forEach(panes, function(pane) {
					pane.active = false;
				});
				pane.active = true;
			};
			this.addPane = function(pane) {
				if (panes.length == 0) {
					$scope.select(pane);
				}
				panes.push(pane);
			};
		}
	}
});
app.directive('tab', function() {
	return {
		restrict: 'E',
		scope: {
			tabTitle: '@'
		},
		transclude: true,
		template: '<div class="tab-content" ng-class="{active: active}" ng-transclude></div>',
		require: '^tabs',
		link: function(scope, element, attrs, tabsCtrl) {
			tabsCtrl.addPane(scope);
		}
	}
});

app.controller('AppCtrl', function($scope) {
	$scope.hBack = function() { 
		window.history.go(-1);
	};
});
app.controller('NavCtrl', function($scope) {
	$scope.navs = [
/*
		{
			'name': 'index',
			'url': '/',
			'text': 'Index'
		},
*/
		{
			'name': 'punters',
			'url': '/punters',
			'text': 'Punters'
		},
		{
			'name': 'films',
			'url': '/films',
			'text': 'Films'
		},
		{
			'name': 'showings',
			'url': '/showings',
			'text': 'Showings'
		},
		{
			'name': 'events',
			'url': '/events',
			'text': 'Ticketed Events'
		},
		{
			'name': 'showingwizard',
			'url': '/showings/create',
			'text': 'Ez-Showing Wizard'
		}
	];

	$scope.navActive = function(navName) {
		if ($scope.navName == navName) return 'active';
		return '';
	}
});
app.controller('IndexCtrl', function($rootScope) {
	$rootScope.navName = 'index';
});
app.controller('EventsCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'events';

	var thisPage = parseInt($routeParams.page, 10);
	if (thisPage != $routeParams.page) {
		$location.search('page', 1);
		return;
	}

	var perPage = parseInt($routeParams.perPage, 10);
	if (isNaN(perPage) || perPage < 5) {
		perPage = 10;
	}
	var sobj = {
		page: thisPage,
		per_page: perPage
	};

	var events = Restangular.all('events');
	var updateEventData = function() {
        	events.getList(sobj).then(function(res) {
			var startRecord = ((thisPage-1) * perPage) + 1;
			var endRecord = (startRecord + res.length) - 1;
			$scope.data = {
				'startAt': startRecord,
				'endAt': endRecord,
				'results': res,
				'next': (res._resultmeta.next ? thisPage+1 : null),
				'previous': (res._resultmeta.previous ? thisPage-1 : null),
				'count': res._resultmeta.count
			}
		});
	};
	updateEventData();

	$scope.search = function(q) {
		sobj.search = q;
		updateEventData();
	};

	$scope.goTo = function(where) {
		if (!where) return;
		$location.search('page', where);
	};

	$scope.buttonClass = function(pageNum) {
		if (!pageNum) return 'default';
		return 'secondary';
	};

	$scope.eventUrl = function(event) {
		return '#/events/' + event.id;
	};
});
app.controller('EventCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'events';

	$scope.loading = true;

	var eventId = parseInt($routeParams.id, 10);

	var event = Restangular.one('events', eventId);
	var updateEventData = function() {
		event.get().then(function(res) {
			$scope.loading = false;
			$scope.data = res;
		});
		$scope.showings = event.getList('showings').$object;
		$scope.tickettypes = event.getList('tickettypes').$object;
	};
	updateEventData();

	$scope.edit = {
		tickettype: {}
	};

	$scope.filmUrl = function(film) {
                var filmId = film.split('/').reverse()[1];
		return '#/films/' + filmId;
	};
	$scope.showingUrl = function(showing) {
		return '#/showings/' + showing.id;
	};

	$scope.editTicketType = function(tickettype) {
		$scope.edit.tickettype.original = tickettype;
		$scope.edit.tickettype.edit = Restangular.copy(tickettype);
	};
	$scope.saveTicketType = function(tickettype) {
		$scope.edit.tickettype.original = $scope.edit.tickettype.edit;
		$scope.edit.tickettype.edit.put().then(updateEventData);
	};
	$scope.deleteTicketType = function(tickettype) {
		tickettype.delete().then(updateEventData);
	};
});
app.controller('ShowingsCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'showings';

	var thisPage = parseInt($routeParams.page, 10);
	if (thisPage != $routeParams.page) {
		$location.search('page', 1);
		return;
	}

	var perPage = parseInt($routeParams.perPage, 10);
	if (isNaN(perPage) || perPage < 5) {
		perPage = 10;
	}
	var sobj = {
		page: thisPage,
		per_page: perPage
	};

	var showings = Restangular.all('showings');
	var updateShowingData = function() {
        	showings.getList(sobj).then(function(res) {
			var startRecord = ((thisPage-1) * perPage) + 1;
			var endRecord = (startRecord + res.length) - 1;
			$scope.data = {
				'startAt': startRecord,
				'endAt': endRecord,
				'results': res,
				'next': (res._resultmeta.next ? thisPage+1 : null),
				'previous': (res._resultmeta.previous ? thisPage-1 : null),
				'count': res._resultmeta.count
			}
		});
	};
	updateShowingData();

	$scope.search = function(q) {
		sobj.search = q;
		updateShowingData();
	};

	$scope.goTo = function(where) {
		if (!where) return;
		$location.search('page', where);
	};

	$scope.buttonClass = function(pageNum) {
		if (!pageNum) return 'default';
		return 'secondary';
	};

	$scope.showingUrl = function(showing) {
		return '#/showings/' + showing.id;
	};
});
app.controller('ShowingCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'showings';

	$scope.loading = true;

	var showingId = parseInt($routeParams.id, 10);

	var showing = Restangular.one('showings', showingId);
	showing.get().then(function(res) {
		$scope.loading = false;
		$scope.data = res;
	});

	$scope.filmUrl = function(film) {
                var filmId = film.split('/').reverse()[1];
		return '#/films/' + filmId;
	};
});
app.controller('FilmsCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'films';

	var thisPage = parseInt($routeParams.page, 10);
	if (thisPage != $routeParams.page) {
		$location.search('page', 1);
		return;
	}

	var perPage = parseInt($routeParams.perPage, 10);
	if (isNaN(perPage) || perPage < 5) {
		perPage = 10;
	}

	var sobj = {
	       page: thisPage,
	       per_page: perPage
	};
	$scope.retrieve = sobj;

	var films = Restangular.all('films');
	var updateFilmData = function() {
        	films.getList(sobj).then(function(res) {
			var startRecord = ((thisPage-1) * perPage) + 1;
			var endRecord = (startRecord + res.length) - 1;
			$scope.data = {
				'startAt': startRecord,
				'endAt': endRecord,
				'results': res,
				'next': (res._resultmeta.next ? thisPage+1 : null),
				'previous': (res._resultmeta.previous ? thisPage-1 : null),
				'count': res._resultmeta.count
			}
		});
	};
	updateFilmData();

	$scope.search = function(q) {
		sobj.search = q;
		updateFilmData();
	};

	$scope.goTo = function(where) {
		if (!where) return;
		$location.search('page', where);
	};

	$scope.buttonClass = function(pageNum) {
		if (!pageNum) return 'default';
		return 'secondary';
	};

	$scope.filmUrl = function(film) {
		return '#/films/' + film.id;
	};

	$scope.addFilm = {
		search: '',
		go: function() {
			$scope.addFilm.searching = true;
			$scope.addFilm.resultsFor = null;
			$scope.addFilm.results = [];
			var st = $scope.addFilm.search;
			films.customGETLIST('search_tmdb', {'query': st}).then(function(res) {
				$scope.addFilm.searching = false;
				$scope.addFilm.resultsFor = st;
				$scope.addFilm.results = res;
			});
		},
		create: function(film) {
			films.post(film).then(function() {
				updateFilmData();
			});
		},
		resultsFor: null,
		results: [],
		addType: 'tmdb'
	};
});
app.controller('FilmCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'films';

	$scope.editing = false;
	$scope.loading = true;

	var filmId = parseInt($routeParams.id, 10);

	var film = Restangular.one('films', filmId);
	film.get().then(function(res) {
		$scope.loading = false;
		$scope.data = res;
	});
	film.getList('showings').then(function(res) {
		$scope.showings = res;
	});

	$scope.remoteUpdate = function() {
		$scope.loading = true;
		film.customPOST({}, "update_remote", {}).then(function(res) {
			$scope.data = res;
			$scope.loading = false;
		});
	};

	$scope.edit = function() {
		$scope.edit_data = Restangular.copy($scope.data);
		$scope.editing = true;
	};

	$scope.cancelEdit = function() {
		$scope.editing = false;
	};
	$scope.saveEdit = function() {
		$scope.data = $scope.edit_data;
		$scope.data.put();
		$scope.editing = false;
	};
});
app.controller('PuntersCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'punters';

	var thisPage = parseInt($routeParams.page, 10);
	if (thisPage != $routeParams.page) {
		$location.search('page', 1);
		return;
	}

	var perPage = parseInt($routeParams.perPage, 10);
	if (isNaN(perPage) || perPage < 5) {
		perPage = 10;
	}

	var searchQuery = $routeParams.q;
	var sobj = {page: thisPage, per_page: perPage};
	if (searchQuery) sobj.search = searchQuery;
	$scope.searchQuery = searchQuery;

	$scope.data = {};

	var punters = Restangular.all('punters');
	var updatePunterData = function() {
		if ($scope.searchQuery) sobj.search = $scope.searchQuery;
		else delete sobj.search;
		punters.getList(sobj).then(function(res) {
			var startRecord = ((thisPage-1) * perPage) + 1;
			var endRecord = (startRecord + res.length) - 1;
			$scope.data = {
				'startAt': startRecord,
				'endAt': endRecord,
				'results': res,
				'next': (res._resultmeta.next ? thisPage+1 : null),
				'previous': (res._resultmeta.previous ? thisPage-1 : null),
				'count': res._resultmeta.count
			}
		});
	};
	updatePunterData();

	$scope.search = function(q) {
		sobj.page = 1;
		updatePunterData();
	};

	$scope.goTo = function(where) {
		if (!where) return;
		$location.search('page', where);
	};

	$scope.buttonClass = function(pageNum) {
		if (!pageNum) return 'default';
		return 'secondary';
	};

	$scope.punterUrl = function(punter) {
		return '#/punters/' + punter.id;
	};
});
app.controller('PunterCtrl', function($rootScope, $scope, $routeParams, $location, Restangular) {
	$rootScope.navName = 'punters';

	$scope.loading = true;

	$scope.punterTypes = [
		{ label: 'Full member', value: 'full' },
		{ label: 'Associate/Life member', value: 'associate' },
		{ label: 'Public', value: 'public' }
	];

	var punterId = parseInt($routeParams.id, 10);

	var punter = Restangular.one('punters', punterId)
	var updateData = function() {
		punter.get().then(function(res) {
			$scope.data = res;
			$scope.loading = false;
		});
		punter.getList('entitlement_details').then(function(res) {
			$scope.entitlement_details = res;
		});
		punter.getList('tickets').then(function(res) {
			$scope.tickets = res;
		});
	};
	updateData();

	$scope.editData = function() {
		$scope.edit_data = Restangular.copy($scope.data);
		$scope.data_editing = true;
	};
	$scope.cancelEditData = function() {
		$scope.data_editing = false;
	};
	$scope.saveEditData = function() {
		$scope.data = $scope.edit_data;
		$scope.edit_data.put().then(updateData);
		$scope.data_editing = false;
	};

	$scope.punterTypeToString = function(type) {
		switch (type) {
			case 'full':
				return "Full member";
			case 'associate':
				return "Associate/life member";
			case 'public':
				return "Public (not a Union member)";
		}
		return "Unknown"
	};

	$scope.entitlementClass = function(en) {
		var classes = ['entitlement'];
		if (en.valid) {
			classes.push('valid');
		} else {
			classes.push('invalid');
		}

		return classes.join(' ');
	};

	$scope.editEntitlementDetail = function(ed) {
		if (!ed.orig)
                        ed.orig = Restangular.copy(ed);
		ed.edit = Restangular.copy(ed.orig);
		ed.editing = true;
	};
	$scope.cancelEditEntitlementDetail = function(ed) {
		ed.editing = false;
	};
	$scope.saveEditEntitlementDetail = function(ed) {
		ed.edit.put().then(updateData);
		for (var n in ed.edit) {
			if (!ed.edit.hasOwnProperty(n)) continue;
			ed[n] = ed.orig[n] = ed.edit[n];
		}
		ed.editing = false;
	};
});

app.controller('ShowingWizardCtrl', function($rootScope, $scope, Restangular, $q, $route) {
	$rootScope.navName = 'showingwizard';

	$scope.step = 1;

	var films = Restangular.all('films');
	var showings = Restangular.all('showings');
	var events = Restangular.all('events');

	var eventTypes = {};
	Restangular.one('event-types', STANDARD_EVENT_TYPE).get().then(function(res) {
		eventTypes[STANDARD_EVENT_TYPE] = res;
	});
	Restangular.one('event-types', DOUBLEBILL_EVENT_TYPE).get().then(function(res) {
		eventTypes[DOUBLEBILL_EVENT_TYPE] = res;
	});

	$scope.restart = function() {
		$route.reload();
	};

	$scope.stepOne = {
		searchFilms: function(query) {
			films.getList({search: query}).then(function(res) {
				console.log(res);
				$scope.stepOne.results = res;
			});
		},
		results: [],
		films: [],
		addFilm: function(film) {
			$scope.stepOne.films.push(Restangular.copy(film));
		},
		next: function(films) {
			$scope.stepTwo.start(films);
		}
	};
	$scope.stepTwo = {
		start: function(films) {
			if (!films.length || films.length < 1) return;
			$scope.stepTwo.films = films;
			$scope.step = 2;
		},
		back: function() {
			$scope.step = 1;
		},
		validDate: new RegExp(/^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/(19|20)\d\d$/),
		validTime: new RegExp(/^(0[0-9]|1[0-9]|2[0-3])(:[0-5][0-9])$/),
		valid: function(film) {
			if (!film) return false;
			if (!film.time || !$scope.stepTwo.validTime.test(film.time)) return false;
			return true;
		},
		formValid: function() {
			for (var i = 0; i < $scope.stepTwo.films.length; i++) {
				if (!$scope.stepTwo.valid($scope.stepTwo.films[i])) return false;
			}
			if (!$scope.stepTwo.date || !$scope.stepTwo.validDate.test($scope.stepTwo.date)) return false;
			return true;
		},
		dateValid: function(date) {
			if (!date || !$scope.stepTwo.validDate.test(date)) return false;
			return true;
		},
		films: [],
		next: function(films, date) {
			for (var i = 0; i < films.length; i++) {
				var film = films[i];
				film.moment = moment(date + " " + film.time, "DD/MM/YYYY HH:mm");
				film.datetime = film.moment.toISOString();
			}
			$scope.stepThree.start(films);
		}
	};
	$scope.stepThree = {
		start: function(films) {
			if (!films || !films.length || films.length < 1) return;
			$scope.stepThree.films = films;
			$scope.step = 3;

			// ok, now we need to build our showings and films:
			var that = $scope.stepThree;
			that.showings = [];
			that.events = [];

			// showings first:
			for (var i = 0; i < films.length; i++) {
				var showing = {
					film: films[i],
					start_time: films[i].datetime
				};
				that.showings.push(showing);
			}

			// now create events for each of those showings...
			var bigEvent = {
				name: '',
				showings: [],
				event_types: [],
				start_time: null
			};
			for (var i = 0; i < that.showings.length; i++) {
				var event = {
					name: that.showings[i].film.name,
					showings: [ that.showings[i] ],
					event_types: [ eventTypes[STANDARD_EVENT_TYPE] ],
					start_time: that.showings[i].start_time,
					ticket_types: eventTypes[STANDARD_EVENT_TYPE].ticket_templates
				};
				that.events.push(event);
				
				if (bigEvent.name != '') {
					if (i != that.showings.length - 1)
						bigEvent.name += ', ';
					else
						bigEvent.name += ' and ';
				}
				bigEvent.name += that.showings[i].film.name;
				bigEvent.showings.push(that.showings[i]);
				var thisMoment = moment(that.showings[i].start_time);
				if (bigEvent.start_time == null || thisMoment.isBefore(bigEvent.start_time)) {
					bigEvent.start_time = that.showings[i].start_time;
				}
			}

			// and one big overarching event, too
			if (that.showings.length != 1) {
				if (bigEvent.showings.length == 2) {
					bigEvent.event_types = [ eventTypes[DOUBLEBILL_EVENT_TYPE] ];
					bigEvent.ticket_types = eventTypes[DOUBLEBILL_EVENT_TYPE].ticket_templates;
				}
				that.events.push(bigEvent);
			}
		},
		back: function() {
			$scope.step = 2;
		},
		next: function() {
			if ($scope.creating) return;
			$scope.creating = true;
			// the server will attempt to help us here
			// if we generate showings, it will AUTOMATICALLY generate a corresponding "simple" event to match
			// however, any overarching events must be manually generated
			var that = $scope.stepThree;
			var promises = [];
			for (var i = 0; i < that.showings.length; i++) {
				var sshowing = that.showings[i];
				var showing = {
					'film': sshowing.film.url,
					'start_time': sshowing.start_time,
				};
				var promise = showings.post(showing);
				promise.then((function(sshowing) {
					return function(res) {
						sshowing.created = true;
						sshowing.created_obj = res;
						return res;
					};
				})(sshowing));
				promises[i] = promise;
			}

			$q.all(promises).then(function() {
				var promises = [];
				for (var i = 0; i < that.events.length; i++) {
					var sevent = that.events[i];
					if (sevent.showings.length == 1) {
						// only generate "complex" events
						sevent.created = true;
						sevent.tickets_created = true;
						continue;
					}
					var event = {
						name: sevent.name,
						start_time: sevent.start_time,
						showings: [],
						event_types: []
					};
					for (var q = 0; q < sevent.showings.length; q++) {
						event.showings.push(sevent.showings[q].created_obj.url);
					}
					for (var q = 0; q < sevent.event_types.length; q++) {
						event.event_types.push(sevent.event_types[q].url);
					}
					var promise = events.post(event);
					promise.then((function(sevent) {
						return function(res) {
							sevent.created = true;
							sevent.created_obj = res;
							res.post('reset_ticket_types_by_event_type/', {}).then(function() {
								sevent.tickets_created = true;
							});
						};
					})(sevent));
					promises.push(promise);
				}

				$q.all(promises).then(function() {
					$scope.step += 1;
				});
			});
		}
	};
});
