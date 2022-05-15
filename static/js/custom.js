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
function myMap() {
    function success(pos) {
        var lat = pos.coords.latitude;
        var lng = pos.coords.longitude;
        var latlng = new google.maps.LatLng(lat, lng);
        var map = new google.maps.Map(document.getElementById("googleMap"), {
            zoom: 17,
            center: latlng
        });
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(35.63339, 139.66166),
            icon: 'static/images/marker.png',
            map: map,
            url: 'http://127.0.0.1:5000/menu'
        });
        var infoWindow = new google.maps.InfoWindow({
            content: '<div class="googleMap"><a href="http://127.0.0.1:5000/menu">VP駒沢大学駅</a></div>'
        });
        marker.addListener('click', function(){
            infoWindow.open(map, marker);
        });
    }
    function fail(error) {
        alert('位置情報の取得に失敗しました');
        var latlng = new google.maps.LatLng(35.6812405, 139.7649361);
        var map = new google.maps.Map(document.getElementById("googleMap"), {
            zoom: 10,
            center: latlng
        });
        marker = new google.maps.Marker({
            position: new google.maps.LatLng(35.63339, 139.66166),
            icon: 'static/images/marker.png',
            map: map,
            url: 'http://127.0.0.1:5000/menu'
        });
        var infoWindow = new google.maps.InfoWindow({
            content: '<div class="googleMap"><a href="http://127.0.0.1:5000/menu">VP駒沢大学駅</a></div>'
        });
        marker.addListener('click', function(){
            infoWindow.open(map, marker);
        });
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