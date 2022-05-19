// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();


// isotope js
$(window).on('load', function () {
    $('.filters_menu li').click(function () {
        $('.filters_menu li').removeClass('active');
        $(this).addClass('active');

        var data = $(this).attr('data-filter');
        $grid.isotope({
            filter: data
        })
    });

    var $grid = $(".grid").isotope({
        itemSelector: ".all",
        percentPosition: false,
        masonry: {
            columnWidth: ".all"
        }
    })
});

// nice select
$(document).ready(function() {
    $('select').niceSelect();
  });

/** google_map js **/
var map;
var marker = [];
var infoWindow = [];

var markerData = []

$(function(){
    $.ajax({
        type: "GET",
        url: "/api/locations",
        dataType: "json",
        success: function(data){
            markerData = data;
            myMap(markerData);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            alert('Error : ' + errorThrown)
        }
    });
});

/*var markerD = [
    {
        name: '駒沢大学',
        lat: 35.63339,
        lng: 139.66166,
        icon: 'static/images/marker.png',
        locationId: '1001'
    }, {
        name: '新町保育園',
        lat: 35.62664,
        lng: 139.65360,
        icon: 'static/images/marker.png',
        locationId: '1002'
    }, {
        name: '深沢小学校',
        lat: 35.627579,
        lng: 139.652410,
        icon: 'static/images/marker.png',
        locationId: '1003'
    }, {
        name: '駒沢公園3号売店',
        lat: 35.627498,
        lng: 139.658775,
        icon: 'static/images/marker.png',
        locationId: '1004'
    }, {
        name: 'Mr.FARMER 駒沢公園店',
        lat: 35.62810,
        lng: 139.65667,
        icon: 'static/images/marker.png',
        locationId: '1005'
    }, {
        name: '駒沢病院',
        lat: 35.63391,
        lng: 139.66060,
        icon: 'static/images/marker.png',
        locationId: '1006'
    }, {
        name: '駒沢小学校',
        lat: 35.63324,
        lng: 139.65795,
        icon: 'static/images/marker.png',
        locationId: '1007'
    }, {
        name: '駒沢バッティングスタジアム',
        lat: 35.62250,
        lng: 139.65666,
        icon: 'static/images/marker.png',
        locationId: '1008'
    }
];*/

function markers(map, markerData) {
    for (var i = 0; i < markerData.length; i++) {
        markerLatLng = new google.maps.LatLng({ lat: markerData[i]['lat'], lng: markerData[i]['lng']});
        marker[i] = new google.maps.Marker({
            position: markerLatLng,
            map: map,
            icon: markerData[i]['icon']
        });
        infoWindow[i] = new google.maps.InfoWindow({
            content: '<div class="googleMap"><a href="/items?locationId=' + markerData[i]['locationId'] + '">' + markerData[i]['locationNameJp'] + '</a></div>' 
        });
        markerEvent(i);
    };
}

function markerEvent(i) {
    marker[i].addListener('click', function() { // マーカーをクリックしたとき
      infoWindow[i].open(map, marker[i]); // 吹き出しの表示
  });
}

function myMap(markerData) {
    function success(pos) {
        var lat = pos.coords.latitude;
        var lng = pos.coords.longitude;
        var latlng = new google.maps.LatLng(lat, lng);
        var map = new google.maps.Map(document.getElementById("googleMap"), {
            zoom: 15,
            center: latlng
        });
        markers(map, markerData);
    }
    function fail(error) {
        alert('位置情報の取得に失敗しました');
        var latlng = new google.maps.LatLng(35.6812405, 139.7649361);
        var map = new google.maps.Map(document.getElementById("googleMap"), {
            zoom: 10,
            center: latlng
        });
        markers(map, markerData);
    }
    navigator.geolocation.getCurrentPosition(success, fail);
}

// client section owl carousel
$(".client_owl-carousel").owlCarousel({
    loop: true,
    margin: 0,
    dots: false,
    nav: true,
    navText: [],
    autoplay: true,
    autoplayHoverPause: true,
    navText: [
        '<i class="fa fa-angle-left" aria-hidden="true"></i>',
        '<i class="fa fa-angle-right" aria-hidden="true"></i>'
    ],
    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1000: {
            items: 2
        }
    }
});