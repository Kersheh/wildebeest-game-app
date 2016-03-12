$(document).ready(function() {
    //initialize game
    getBoard();

    // render current board to app
    function renderBoard(board) {
        var table = $("<table></table>");
        var x, y;
        for(i = 0; i < 11; i++) {
            x = $("<tr></tr>").addClass("tile x " + i);
            for(j = 0; j < 11; j++) {
                y = $("<td align=\"center\"></td>").addClass("tile y " + j).text(board[i][j]);
                x.append(y);
            }
            table.append(x);
        }
        $("#board").append(table);
    }

    // retrieve current board from server
    function getBoard() {
        $.ajax({
            type: "GET",
            url: "api/v1.0/board",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                renderBoard(data);
            },
            error: function(jqXHR, status) {
                console.log("Error status: " + status);
            }
        });
    }
});