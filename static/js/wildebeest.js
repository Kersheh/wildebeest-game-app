$(document).ready(function() {
    //initialize game
    var current_board;
    newBoard();

    // render current board to app
    function renderBoard(board) {
        var cell;
        for(i = 0; i < 11; i++) {
            for(j = 0; j < 11; j++) {
                $("td[x$=\"" + i + "\"][y$=\"" + j + "\"]").text(board[i][j]);
            }
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
                renderBoard(current_board["board"]);
                setplayerTurn();
            },
            error: function(jqXHR, status) {
                console.log("Error retrieving board from server. Status: " + status);
            }
        });
    }

    // reset board button
    $("#reset-board").click(function() {
        current_board = newBoard();
        $("#winner").text("");
        $("#invalid-move").popover("hide");
        renderBoard(current_board["board"]);
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

    // commit move to board through server
    function setMove(x, y, x_new, y_new) {
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
                renderBoard(current_board["board"]);
                setplayerTurn();
                if(isWinner()) return;
                disableInterface();
                loading();
                getMoveAI();
            },
            error: function(jqXHR, status) {
                $("#invalid-move").popover("show");
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
        // $.get("api/v1.0/move/ai", function(data, status) {
        //     current_board = data;
        //     renderBoard(current_board["board"]);
        //     setplayerTurn();
        //     if(isWinner()) return;
        //     enableInterface();
        //     loadingComplete();
        // });
        $.ajax({
            type: "POST",
            data: JSON.stringify(current_board),
            url: "api/v1.0/move/ai",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                current_board = data;
                renderBoard(current_board["board"]);
                setplayerTurn();
                if(isWinner()) return;
                enableInterface();
                loadingComplete();
            }
        });
    }

    

    // check if winner
    function isWinner() {
        var w = false, b = false;
        for(i = 0; i < 11; i++) {
            for(j = 0; j < 11; j++) {
                if(current_board["board"][i][j] == "K" || current_board["board"][i][j] == "W") w = true;
                if(current_board["board"][i][j] == "k" || current_board["board"][i][j] == "w") b = true;
            }
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
        $("#loading").addClass("glyphicon-refresh glyphicon-refresh-animate");
    }

    // remove loading animation
    function loadingComplete() {
        $("#loading").removeClass("glyphicon-refresh glyphicon-refresh-animate");
    }
});