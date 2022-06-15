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
$(document).ready(function () {
    $('select').niceSelect();
});

// google_map js
var map;
var markerData = []
var marker = [];
var infoWindow = [];

$(function () {
    $.ajax({
        type: "GET",
        url: "/api/locations?limit=1000",
        dataType: "json",
        success: function (data) {
            markerData = data['locations'];
            myMap(markerData);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert('Error : ' + errorThrown)
        }
    });
});

function markers(map, markerData) {
    for (var i = 0; i < markerData.length; i++) {
        markerLatLng = new google.maps.LatLng({ lat: markerData[i]['lat'], lng: markerData[i]['lng'] });
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
    marker[i].addListener('click', function () {
        infoWindow[i].open(map, marker[i]);
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