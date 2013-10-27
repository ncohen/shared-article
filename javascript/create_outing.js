var locations = {};

function makeRequest(query, callback) {
  var query = query + ('&callback=?');
  $.getJSON(query, {}, callback);
}

function autoCompleteVenue(s, callback){
  
  makeRequest('https://api.foursquare.com/v2/venues/suggestcompletion?query=' + s + '&near=New York, NY&limit=10&client_id=F0FKSGKKPTV3ISJMPLUXURLMQTELV4QDU1U33Z0CSRIXQZQC&client_secret=0LRRQBSDPBJIB2QUWVDVWA1WB0NRLTJFEOIXCGNDMXAAWKWS&v=20130901',
                     function(response) { callback(response)  });
}

function grabUrl(a, callback){
	makeRequest('https://api.foursquare.com/v2/venues/' + a + '?client_id=F0FKSGKKPTV3ISJMPLUXURLMQTELV4QDU1U33Z0CSRIXQZQC&client_secret=0LRRQBSDPBJIB2QUWVDVWA1WB0NRLTJFEOIXCGNDMXAAWKWS&v=20130901',
                     function(response) { callback(response)  });

}

function set_url(response){

	a = response['response']
	url = a['venue']['canonicalUrl'];

	document.getElementById('url').value = url;
}

function handle_autocomplete(response){
	console.log(response['response']['minivenues'].length);
	var a = response['response']['minivenues'];

	availableTags = [];
	for(var i=0; i<a.length; i++){
		var short_name = String(a[i]['name']) + ' - ' + String(a[i]['location']['address']);
		availableTags.push(short_name);
		locations[short_name] = a[i]['id'];

    	$( "#tags" ).autocomplete({
   		source: availableTags});	
	}
}