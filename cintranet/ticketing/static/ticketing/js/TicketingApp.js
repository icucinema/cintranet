var app = angular.module('TicketingApp', [
	'ngRoute',
	'ngResource'
]);

app.constant('djurl', __djurls);

app.config(['djurl', '$routeProvider', '$httpProvider', function(djurl, $routeProvider, $httpProvider) {
	$routeProvider.
		when('/', {
			templateUrl: djurl.partial_root + 'index.html',
			controller: 'IndexCtrl'
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
app.controller('PuntersCtrl', function($rootScope, $scope, $routeParams, $location, Punter) {
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
	
	Punter.query({page: thisPage, per_page: perPage}, function(res) {
		var startRecord = ((thisPage-1) * perPage) + 1;
		var endRecord = (startRecord + res.results.length) - 1;
		$scope.data = {
			'startAt': startRecord,
			'endAt': endRecord,
			'results': res.results,
			'next': (res.next ? thisPage+1 : null),
			'previous': (res.previous ? thisPage-1 : null),
			'count': res.count
		}
	});

	$scope.goTo = function(where) {
		if (!where) return;
		$location.search('page', where);
	};

	$scope.buttonClass = function(pageNum) {
		if (!pageNum) return 'default';
		return 'secondary';
	}

	$scope.punterUrl = function(punter) {
		return '#/punters/' + punter.id;
	};
});
app.controller('PunterCtrl', function($rootScope, $scope, $routeParams, $location, Punter) {
	$rootScope.navName = 'punters';

	$scope.loading = true;

	var punterId = parseInt($routeParams.id, 10);

	Punter.get({id: punterId}, function(res) {
		$scope.data = res;
		$scope.loading = false;
	});

	$scope.punterTypeToString = function(type) {
		switch (type) {
			case 0:
				return "Full member";
			case 1:
				return "Associate/life member";
			case 2:
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
});