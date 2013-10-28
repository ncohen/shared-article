  (function() {
    var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
    po.src = 'https://apis.google.com/js/plusone.js?onload=onLoadCallback';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
  })();

//bind to all links
$('#submit').click( function() {
   //get the url
   var url = $(this).prop('href');
   //send the url to your server
   $.ajax({
        type: "POST",
        url: "http://singlecalendar.appspot.com/create_new_outing",
        data: {url: url, post_text: "test", participants: "test2"}
   });
});