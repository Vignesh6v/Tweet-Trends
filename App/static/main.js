var map, pointarray, heatmap;
var taxiData = [];
var tweet_text = [];
var sentiment_response = [];
var gmarkers = [];

var cur_zoom = 2;
var cur_centre = new google.maps.LatLng(40.52, 4.34);

var is_bounds_changed = false;

function initialize() {

        if(map) cur_zoom = map.getZoom();

        var mapOptions = {
            zoom: cur_zoom,
            center: new google.maps.LatLng(40.52, 4.34),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

        google.maps.event.addListener(map, "rightclick", function(event) {
            if (document.getElementById('heatMap').checked) {
                heat();
            } else if (document.getElementById('pinMap').checked) {
                pin();
            }
        });

        google.maps.event.addListener(map, "click", function(event) {
            var lat1_deg = event.latLng.lat();
            var lng1_deg = event.latLng.lng();
            cur_centre =  new google.maps.LatLng(lat1_deg, lng1_deg);

            user_radius = $('#input_radius').val(); //in kms
            earth_radius = 6371; //in kms
            k = 0;
            newTaxiData = [];

            for (i = 0; i < taxiData.length; i++) {
                lat1 = (Math.PI * lat1_deg) / 180;
                lng1 = (Math.PI * lng1_deg) / 180;

                var lat2 = taxiData[i].lat();
                var lng2 = taxiData[i].lng();
                lat2 = (Math.PI * lat2) / 180;
                lng2 = (Math.PI * lng2) / 180;

                dist = Math.acos((Math.sin(lat1) * Math.sin(lat2)) + (Math.cos(lat1) * Math.cos(lat2) * Math.cos(lng1 - lng2))) * earth_radius;
                if (dist <= user_radius) {
                    newTaxiData[k++] = taxiData[i];
                }
            }

            initialize();

            var myCity = new google.maps.Circle({
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: '#FF0000',
                fillOpacity: 0.25,
                map: map,
                center: new google.maps.LatLng(lat1_deg, lng1_deg),
                radius: user_radius * 1000
            });

            if (document.getElementById('heatMap').checked) {
                heatNew(newTaxiData);
            } else if (document.getElementById('pinMap').checked) {
                pinNew(newTaxiData);
            }

        });


    } //end of initialize


function editMarkers(marker,i) {

    if (sentiment_response[i].toLowerCase() === "positive")
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
    else if (sentiment_response[i].toLowerCase() === "negative")
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/red-dot.png');
    else
        marker.setIcon('http://maps.google.com/mapfiles/ms/icons/blue-dot.png');


      var contentString =
          '<div id="content">'+
            '<div id="siteNotice"></div>'+
            '<h1 id="firstHeading" class="firstHeading">'+sentiment_response[i]+'</h1>'+
            '<div id="bodyContent">'+
                '<p>'+tweet_text[i]+'</p>'+
            '</div>'+
          '</div>';

      var infowindow = new google.maps.InfoWindow({
        content: contentString
      });


     marker.addListener('click', function() {
        infowindow.open(map, marker);
      });

}

function pin() {
    initialize();
    for (i = 0; i < taxiData.length; i++) {
        var latD = taxiData[i].lat();
        var lngD = taxiData[i].lng();
        marker = new google.maps.Marker({
            //animation: google.maps.Animation.DROP,
            position: new google.maps.LatLng(latD, lngD),
            map: map
        });
        editMarkers(marker,i);
    }

}

function pinNew(newTaxiData) {
    for (i = 0; i < newTaxiData.length; i++) {
        var latD = newTaxiData[i].lat();
        var lngD = newTaxiData[i].lng();
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(latD, lngD),
            map: map
        });
        editMarkers(marker,i);
    }
}


function heat() {
    initialize();
    var pointArray = new google.maps.MVCArray(taxiData);
    heatmap = new google.maps.visualization.HeatmapLayer({
        data: pointArray,
        radius: 25
    });
    heatmap.setMap(map);
}


function heatNew(newTaxiData) {
    var pointArray = new google.maps.MVCArray(newTaxiData);
    heatmap = new google.maps.visualization.HeatmapLayer({
        data: pointArray,
        radius: 25
    });
    heatmap.setMap(map);
}



$(document).on('click', '.toggle-button', function() {
    $(this).toggleClass('toggle-button-selected');
});


google.maps.event.addDomListener(window, 'load', initialize);


function elasticsearch(search_key_data) {
    if (search_key_data == "- Select Keyword -") {
        taxiData = [];
        tweet_text = []
        sentiment_response = []
        initialize();
    } else {
        $("#search_key").val(search_key_data);
        var searchK = $('#search_key').val()

        $.ajax({
            url: '/search',
            data: $('form').serialize(),
            type: 'GET',
            success: function(response) {
                //console.log(response);

                var jsonResponse = $.parseJSON(response);

                taxiData = []
                tweet_text = []
                sentiment_response = []

                for (var i = 0; i < jsonResponse.length; ++i) {
                    console.log(jsonResponse);
                    taxiData[i] = new google.maps.LatLng(jsonResponse[i].latitude, jsonResponse[i].longitude);
                    tweet_text[i] = jsonResponse[i].tweet_text;
                    sentiment_response[i] = jsonResponse[i].sentiment_response;
                }


                if (document.getElementById('heatMap').checked) {
                    heat();
                } else if (document.getElementById('pinMap').checked) {
                    pin();
                }

            },
            error: function(error) {
                console.log(error);
            }
        });

    }

}
