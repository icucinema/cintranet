var app = angular.module('TicketingApp', [
	'ngRoute',
	'ngResource',
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

app.factory('Punter', ['$resource', 'djurl',
	function($resource, djurl) {
		return $resource(
			djurl.api_root + 'punters/:id/', {},
			{
				query: {
					method: "GET",
					isArray: false
				}
			}
		);
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
		{
			'name': 'index',
			'url': '/',
			'text': 'Index'
		},
		{
			'name': 'punters',
			'url': '/punters',
			'text': 'Punters'
		},
		{
			'name': 'films',
			'url': '/films',
			'text': 'Films'
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

	var films = Restangular.all('films');
	var updateFilmData = function() {
        	films.getList({page: thisPage, per_page: perPage}).then(function(res) {
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

	$scope.loading = true;
	$scope.editing = false;

	var filmId = parseInt($routeParams.id, 10);

	var film = Restangular.one('films', filmId);
	film.get().then(function(res) {
		$scope.loading = false;
		$scope.data = res;
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

	$scope.data = {};

	var punters = Restangular.all('punters');
	punters.getList({page: thisPage, per_page: perPage}).then(function(res) {
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

app.controller('ShowingWizard', function($rootScope, $scope, $routeParams, $location, Restangular) {}) 
