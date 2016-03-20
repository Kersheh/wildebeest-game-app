$(document).ready(function() {
    //initialize game
    var current_board;
    newBoard();
    $("#player-tag").popover("show");
    $("#ai-tag").popover("show");

    // render current board to app
    function renderBoard(pieces) {
        // clear pieces
        $("td").attr("class", "");
        for(i = 0; i < 11; i++) {
            for(j = 0; j < 11; j++) {
                $("td[x=\"" + i + "\"][y=\"" + j + "\"]").text("");
            }
        }
        // update special tiles
        $("td[x=3][y=1]").html("<span class=\"special glyphicon glyphicon-circle-arrow-right td-glyphicon rotate-dr\"></span>");
        $("td[x=3][y=9]").html("<span class=\"special glyphicon glyphicon-circle-arrow-left td-glyphicon\"></span>");
        $("td[x=7][y=1]").html("<span class=\"special glyphicon glyphicon-circle-arrow-right td-glyphicon rotate-ur\"></span>");
        $("td[x=7][y=9]").html("<span class=\"special glyphicon glyphicon-circle-arrow-left td-glyphicon\"></span>");
        $("td[x=5][y=5]").html("<span class=\"special glyphicon glyphicon-record td-glyphicon\"> </span>");
        // add pieces
        var id, x, y;
        for(key in pieces) {
            x = "\"" + pieces[key]["x"] + "\"";
            y = "\"" + pieces[key]["y"] + "\""
            id = pieces[key]["id"];
            glyph = getGlyph(id.toUpperCase());
            $("td[x=" + x + "][y=" + y + "]").text("");
            if(id == id.toUpperCase()) {
                $("td[x=" + x + "][y=" + y + "]").addClass("white_p glyphicon td-glyphicon " + glyph);
            }
            else {
                $("td[x=" + x + "][y=" + y + "]").addClass("black_p glyphicon td-glyphicon " + glyph);
            }
        }
    }

    // return glyph name based on piece id
    function getGlyph(id) {
        switch(id) {
            case "R":
                return "glyphicon-tower";
            case "N":
                return "glyphicon-knight"
            case "Z":
                return "glyphicon-cloud";
            case "B":
                return "glyphicon-bishop"
            case "O":
                return "glyphicon-queen";
            case "E":
                return "glyphicon-queen"; //find replacement
            case "K":
                return "glyphicon-king";
            case "W":
                return "glyphicon-king"; //find replacement
            case "X":
                return "glyphicon-tint";
            case "C":
                return "glyphicon-plane"
            case "G":
                return "glyphicon-wrench";
            case "P":
                return "glyphicon-pawn";
            case "S":
                return "glyphicon-fire"
            case "J":
                return "glyphicon-glass";
            default:
                return "";
        }
    }

    // retrieve new board from server
    function newBoard() {
        $.ajax({
            type: "GET",
            url: "api/v1.0/board/reset",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                current_board = data;
                renderBoard(current_board["pieces"]);
                setplayerTurn();
            },
            error: function(jqXHR, status) {
                console.log("Error retrieving board from server. Status: " + status);
            }
        });
    }

    // reset board button
    $("#reset-board").click(function() {
        newBoard();
        $("#winner").text("");
        $("#invalid-move").popover("hide");
        renderBoard(current_board["pieces"]);
        setplayerTurn();
        enableInterface();
        loadingComplete();
    });

    // set visual queue for player turn
    function setplayerTurn() {
        $("#turn").text(current_board["player_turn"]);
    }

    // submit move button
    $("#set-move").click(function() {
        setMove($("#move-current-x").val(), $("#move-current-y").val(), $("#move-new-x").val(), $("#move-new-y").val());
    });

    // client-side check if player is moving enemy piece
    function friendlyPiece(x, y) {
        var cell = $("td[x=\"" + x + "\"][y=\"" + y + "\"]").text()
        if(cell == cell.toUpperCase()) return true;
        return false;
    }

    // commit move to board through server
    function setMove(x, y, x_new, y_new) {
        if(!friendlyPiece(x, y)) {
            $("#invalid-move").popover("show");
            return;
        }
        move_url = "api/v1.0/move/" + x + "x" + y + "x" + x_new + "x" + y_new;
        $.ajax({
            type: "POST",
            url: move_url,
            data: JSON.stringify(current_board),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                current_board = data;
                $("#invalid-move").popover("hide");
                renderBoard(current_board["pieces"]);
                setplayerTurn();
                if(isWinner(current_board["pieces"])) return;
                disableInterface();
                loading();
                getMoveAI();
            },
            statusCode: {
                400: function () {
                    $("#invalid-move").popover("show");
                }
            }
        });
    }

    // retrieve AI move from server
    function getMoveAI() {
        $.ajax({
            type: "POST",
            data: JSON.stringify(current_board),
            url: "api/v1.0/move/ai",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                current_board = data;
                renderBoard(current_board["pieces"]);
                setplayerTurn();
                if(isWinner(current_board["pieces"])) return;
                enableInterface();
                loadingComplete();
            }
        });
    }

    // check if winner
    function isWinner(pieces) {
        var w = false, b = false;
        for(key in pieces) {
            if(pieces[key]["id"] == "K" || pieces[key]["id"] == "W") w = true;
            if(pieces[key]["id"] == "k" || pieces[key]["id"] == "w") b = true;
        }
        if(w == true && b == true) return false;
        if(w == true && b == false) $("#winner").text("White wins!");
        if(w == false && b == true) $("#winner").text("Black wins!");
        if(w == false && b == false) $("#winner").text("Tie game!");
        loadingComplete();
        disableInterface();
        return true;
    }

    // disable interface
    function disableInterface() {
        $("#move-current-x").prop("disabled", true);
        $("#move-current-y").prop("disabled", true);
        $("#move-new-x").prop("disabled", true);
        $("#move-new-y").prop("disabled", true);
        $("#set-move").addClass("disabled");
    }

    // enable interface
    function enableInterface() {
        $("#move-current-x").prop("disabled", false);
        $("#move-current-y").prop("disabled", false);
        $("#move-new-x").prop("disabled", false);
        $("#move-new-y").prop("disabled", false);
        $("#set-move").removeClass("disabled");
    }

    // loading animation
    function loading() {
        $("#loading").removeClass("glyphicon-resize-horizontal");
        $("#loading").addClass("glyphicon-refresh glyphicon-refresh-animate");
    }

    // remove loading animation
    function loadingComplete() {
        $("#loading").removeClass("glyphicon-refresh glyphicon-refresh-animate");
        $("#loading").addClass("glyphicon-resize-horizontal");
    }

    // pressing enter submits move
    $("input").keyup(function(event) {
        if(event.keyCode == 13) $("#set-move").click();
    });
});