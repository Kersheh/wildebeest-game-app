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
    // function renderBoard(board) {
    //     var table = $("<table></table>");
    //     var x, y;
    //     for(i = 0; i < 12; i++) {
    //         x = $("<tr></tr>").addClass("tile").attr("x", i);
    //         if(i == 0) x.append("<td align=\"center\"></td>").text("x");
    //         for(j = 0; j < 12; j++) {
    //             if(j == 0 && i != 0) {
    //                 x.append("<td align=\"center\"></td>").text(i);
    //             }
    //             if(j == 0) {
    //                 if(j == 11) continue;
    //                 y = $("<td align=\"center\"></td>").text(j);
    //             }
    //             else {
    //                 y = $("<td align=\"center\" id=\"piece\"></td>").addClass("tile").attr("y", j).text(board[i - 1][j - 1]);
    //             }
    //             x.append(y);
    //         }
    //         table.append(x);
    //     }
    //     $(".board").append(table);
    // }

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

    $(function() {
        $("#piece").draggable();
    });
});