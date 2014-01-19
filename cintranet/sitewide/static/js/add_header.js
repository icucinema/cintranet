(function() {
	var xhr = new XMLHttpRequest();
	xhr.onload = function() {
		// add the header markup
		var headerEl = document.createElement('header');
		headerEl.innerHTML = this.responseText;
		var f = document.body.childNodes[0];
		if (f)
			document.body.insertBefore(headerEl, f);
		else
			document.body.appendChild(f);
	};
	xhr.withCredentials = true;
	xhr.open("GET", "https://staff.wide.icucinema.co.uk/remoteheader/", true);
	xhr.send();

	// add the header CSS
	var cssEl = document.createElement('link');
	cssEl.type = 'text/css';
	cssEl.rel = 'stylesheet';
	cssEl.href = '//staff.wide.icucinema.co.uk/static/css/remote_header.css';
	document.head.appendChild(cssEl);
})();
