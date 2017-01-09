var currentSelection;
var rooms;
var available = [];
$.ajaxSetup({async: false});
$.get(
    "/rooms/chad",
    function (data) {
        rooms = JSON.parse(data);
    }
);

$(window).ready(function () {
    populateAvailable(rooms);
    var g = Snap('#svg');
    Snap.load("static/chads.svg", function (f) {
        g.append(f);
        var rooms = selectAvailable();
        rooms.forEach(function (room) {
            room.click(function (evt) {
                clickRoom(evt);

            });
            room.attr({
                fill: 'white'
            });
        });
    });

    function highlight(room) {
        room.attr({
            fill: '#4FC3F7'
        });
        var rooms = selectAvailable();
        var i = rooms.indexOf(room);
        if (i > -1) {
            rooms.splice(i, 1);
        }

        rooms.forEach(function (room) {
            room.attr({
                fill: 'white'
            });
        });
    }

    function clickRoom(evt) {
        var room = g.select('#' + evt.target.id);
        currentSelection = room.node.id.slice(-2);
        highlight(room);
        updateDesc(currentSelection);
    }

    function selectAvailable() {
        var availRooms = [];
        available.forEach(function (aRoom) {
            var room = g.select('#' + aRoom);
            availRooms.push(room);
        });
        return availRooms;
    }
});

function populateAvailable(rooms) {
    rooms.forEach(function (room) {
        var number = room.room;
        var id = "room" + number;
        if (room.available != false) {
            available.push(id);
        }
    });
}

function updateDesc(number) {
    var band;
    var photo;
    rooms.forEach(function (room) {
        if (room.room === number) {
            band = room.band;
            photo = room.photo;
        }
    });
    $('#band').text('Band: ' + band);
    $('#selection').val(number);
    $('#photo').attr("src", '/roomimages/' + photo);
}
