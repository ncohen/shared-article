function Forecast(apiKey, authUrl, apiUrl) {
 this.apiUrl = apiUrl; /*
  if ($.bbq.getState('access_token')) {
    // If there is a token in the state, consume it
    this.token = $.bbq.getState('access_token');
    $.bbq.pushState({}, 2)
  } else if ($.bbq.getState('error')) {
  } else {
    this.doAuthRedirect(authUrl, apiKey);
  }*/
}

var count = 0;

Forecast.prototype.doAuthRedirect = function(authUrl, apiKey) {
  var redirect = window.location.href.replace(window.location.hash, '');
  var url = authUrl + '?key=' + apiKey +
      '&redirect_uri=https://singlecalendar.appspot.com/' + //encodeURIComponent(redirect) + 'oauth2callback' + 
      '&state=' + encodeURIComponent($.bbq.getState('req') || 'users/self');
  window.location.href = url;
};

Forecast.prototype.makeRequest2 = function(query, callback) {
  var query = query;
  $.getJSON("http://i.wxbug.net/REST/Direct/" + query, {}, callback);
};

Forecast.prototype.getWeather = function(callback) {
	this.makeRequest2('GetForecast.ashx?zip=10069&nf=7&ih=1&ht=t&ht=i&ht=d&ht=cp&api_key=5kpnehsmrr93t6uuzm6brxhc&f=?',
                     function(response) { callback(response['forecastList'])  });
};

function Weather(apiKey, authUrl, apiUrl) {
	this.forecast = new Forecast(apiKey, authUrl, apiUrl);
	this.hourlyWeatherForecast = [];
	this.dailyWeatherForecast = [];
	this.offset = 4;
	this.today = '';
}

Weather.prototype.getFiveDayWeather = function() {
//	this.forecast
	this.forecast.getWeather(bind(this.processWeather, this));
}

Weather.prototype.processWeather = function(array){
	this.today = array[0]['dayTitle'];
	
	for(var i = 0; i < array.length; i++){
		var singleDay = array[i];
		var dayTitle = singleDay['dayTitle'];

		
		if(i > 0){
			var dayObj = {};
			var nightObj = {};
			if(singleDay['hasDay'] == true){
				dayObj['dayTitle'] = dayTitle;
				dayObj['description'] = singleDay['dayDesc'];
				dayObj['icon'] = singleDay['dayIcon'];
				dayObj['pred'] = singleDay['dayPred'];
				dayObj['temperature'] = singleDay['high'];
				dayObj['type'] = 'Day';
				this.dailyWeatherForecast.push(dayObj);
			}
			
			if(singleDay['hasNight'] == true){
				nightObj['dayTitle'] = dayTitle;
				nightObj['description'] = singleDay['nightDesc'];
				nightObj['icon'] = singleDay['nightIcon'];
				nightObj['pred'] = singleDay['nightPred'];
				nightObj['temperature'] = singleDay['low'];
				nightObj['type'] = 'Night';
				this.dailyWeatherForecast.push(nightObj);
			}
		}
		
		if(singleDay['hourly'] != null){
			var hourList = singleDay['hourly'];
			for(var j = 0; j < hourList.length; j++ ){
				var a = hourList[j];
				var dateTime = a['dateTime'];
				var obj = {};
				obj['dayTitle'] = dayTitle;
				obj['dateTime'] = dateTime;
				obj['temperature'] = a['temperature'];
				obj['description'] = a['desc'];
				obj['image'] = a['icon'];
				obj['chancePrecipitation'] = a['chancePrecip'];
				this.hourlyWeatherForecast.push(obj);
			}
		}
	}
	
	this.displayWeather();
}

Weather.prototype.displayDailyForecasts = function() {
	
	for(var i = 0; i < this.dailyWeatherForecast.length; i++){
		var a = this.dailyWeatherForecast[i];
		var day = a['dayTitle'];
		var time = a['type'];
		var temperature = a['temperature'];
		var icon = a['icon'];
		var prediction = a['pred'];
		
		$('#weather').append('<div class="dayWeather"><span class="weatherTop"><span class="weatherItem" id="date">' + day + ' ' + time + 
		'</span><span class="weatherItem" id="high">' + 
		temperature + '&deg</span></span><img class="image" src="http://img.weather.weatherbug.com/forecast/icons/localized/500x420/en/opaq/' + 
		icon + '.png" ><p class="weatherItem prediction">' + prediction + '</p></div>');
	}
}

Weather.prototype.displayWeather = function() {
		
	for(var i = 0; i < this.hourlyWeatherForecast.length; i++){
		var b = this.hourlyWeatherForecast[i];
		if(b['dayTitle'] == this.today){
			var dateTime = b['dateTime'];
			var adjustedDateTime = convertTimeZone(dateTime, this.offset); 
			var dateArray = convertDate(adjustedDateTime);

			var dayNumber = dateArray[0];
			var day = findDay(dayNumber);
			var hour = dateArray[1];
			var hourConverted = formatHour(hour);

			$('#weather').append('<div class="dayWeather"><span class="weatherTop" id="'+ count + '"><span class="weatherItem" id="date">' + day + ' ' + hourConverted + 
			'</span><span class="weatherItem" id="high">' + 
			b['temperature'] + '&deg</span><span class="weatherItemPrecip" id="precip' + adjustedDateTime + '">' + b['chancePrecipitation'] +  '%</span></span><img class="image" src="http://img.weather.weatherbug.com/forecast/icons/localized/500x420/en/opaq/' + 
			b['image'] + '.png" ></div>');

			if(b['chancePrecipitation'] > 50){
				$('#precip' + adjustedDateTime).css('background-color', 'yellow');
			}

			count+=1;
		}		
	}
	
	this.displayDailyForecasts();
	
}

// HELPER FUNCTIONS

function convertDate(utc) {
	var utc = parseInt(utc);
	var date = new Date(utc);
	var day = date.getDay();
	var hours = date.getHours();
	var arr = [];
	arr.push(day);
	arr.push(hours);
	return arr;
}

function findDay(num) {
	var x = '';
	
	switch (num)
	{
		case 0:
		  x="Sunday";
		  break;
		case 1:
		  x="Monday";
		  break;
		case 2:
		  x="Tuesday";
		  break;
		case 3:
		  x="Wednesday";
		  break;
		case 4:
		  x="Thursday";
		  break;
		case 5:
		  x="Friday";
		  break;
		case 6:
		  x="Saturday";
		  break;
	}
	
	return x;
}

function convertTimeZone(dateTime, offset) {
	var offsetNum = offset * 3600000;
	var newDateTime = dateTime + offsetNum;
	return newDateTime;
}

//make cleaner
function formatHour(hour) {
	var hour = parseInt(hour);
	var formattedHour = '';
	
	if(hour == 0){
		formattedHour = 12 + 'am';
	}
	
	else if(hour < 12){
		formattedHour = hour + 'am';
	}
	else if(hour == 12){
		formattedHour = hour + 'pm';
	}
	
	else if(hour < 24){
		formattedHour = hour - 12;
		formattedHour = formattedHour + 'pm';
	}
	else{
		formattedHour = hour - 12;
		formattedHour = formattedHour + 'am';
	}
	
	return formattedHour;
}



$(function() {
	var weather = new Weather("5kpnehsmrr93t6uuzm6brxhc", "http://i.wxbug.net/REST/Direct/", "http://i.wxbug.net/REST/Direct/");
	weather.getFiveDayWeather();

/*
	var scrollCount = 0;
	$(window).scroll(function(e){ 
	  $el = $('#0'); 
	  if ($(this).scrollTop() > 0 && $el.css('position') != 'fixed'){ 
	    $('#0').css({'position': 'fixed', 'top': '0px'}); 
	  } 
	});
	
	$(window).scroll(function(e){ 
	  $el = $('#1'); 
	  if ($(this).scrollTop() > 0 && $el.css('position') != 'fixed'){ 
	    $('#1').css({'position': 'fixed', 'top': '0px'}); 
	  } 
	});
	*/
	
})
