$(document).ready(function() {
    //initialize game
    getBoard();

    // render current board to app
    function renderBoard(board) {
        var cell;
        for(i = 0; i < 11; i++) {
            for(j = 0; j < 11; j++) {
                $("td[x$=\"" + i + "\"][y$=\"" + j + "\"]").text(board[i][j]);
            }
        }
    }

    // retrieve current board from server
    function getBoard() {
        $.ajax({
            type: "GET",
            url: "api/v1.0/board",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                renderBoard(data["board"]);
                setplayerTurn(data["player_turn"]);
            },
            error: function(jqXHR, status) {
                console.log("Error status: " + status);
            }
        });
    }

    // set visual queue for player turn
    function setplayerTurn(turn) {
        $("#turn").text(turn);
    }

    // submit move button
    $("#set-move").click(function() {
        setMove($("#move-current-x").val(), $("#move-current-y").val(), $("#move-new-x").val(), $("#move-new-y").val());
    });

    // commit move to board through server
    function setMove(x, y, x_new, y_new) {
        move_url = "api/v1.0/move/" + x + "x" + y + "x" + x_new + "x" + y_new;
        $.ajax({
            type: "GET",
            url: move_url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                $("#invalid-move").popover("hide");
                renderBoard(data["board"]);
                setplayerTurn(data["player_turn"]);
                if(isWinner(data["board"])) return;
                disableInterface();
                loading();
            },
            error: function(jqXHR, status) {
                $("#invalid-move").popover("show");
            },
            statusCode: {
                400: function () {
                    console.log("test");
                    $("#invalid-move").popover("show");
                }
            }
        });
    }

    // reset board through server
    $("#reset-board").click(function() {
        $.ajax({
            type: "GET",
            url: "api/v1.0/board/reset",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                $("#winner").text("");
                $("#invalid-move").popover("hide");
                renderBoard(data["board"]);
                setplayerTurn(data["player_turn"]);
                enableInterface();
                loadingComplete();
            }
        });
    });

    // check if winner
    function isWinner(board) {
        var w = false, b = false;
        for(i = 0; i < 11; i++) {
            for(j = 0; j < 11; j++) {
                if(board[i][j] == "K" || board[i][j] == "W") w = true;
                if(board[i][j] == "k" || board[i][j] == "w") b = true;
            }
        }
        if(w == true && b == true) return false;
        if(w == true && b == false) $("#winner").text("White wins!");
        if(w == false && b == true) $("#winner").text("Black wins!");
        if(w == false && b == false) $("#winner").text("Tie game!");
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
        $("#loading").addClass("glyphicon-refresh glyphicon-refresh-animate");
    }

    // remove loading animation
    function loadingComplete() {
        $("#loading").removeClass("glyphicon-refresh glyphicon-refresh-animate");
    }
});