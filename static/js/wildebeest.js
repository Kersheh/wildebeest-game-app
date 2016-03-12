$(document).ready(function() {
    function initBoard() {
        var table = $("<table></table>");
        var x, y;
        for(i = 0; i < 11; i++) {
            x = $("<tr></tr>").addClass("tile x " + i);
            for(j = 0; j < 11; j++) {
                y = $("<td></td>").addClass("tile y " + j).text("x");
                x.append(y);
            }
            table.append(x);
        }
        $("#board").append(table);
    }
    initBoard();

    function loading() {
        $("#request-search").html("<i class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></i>");
    }

    /* remove loading animation */
    function loadingComplete() {
        $("#request-search").html("<i class=\"glyphicon glyphicon-search\"></i>");
    }

    /* hide popover on rezize */
    $(window).resize(function() {
        $(".todo-list").hide();
        $("#error").popover('hide');
    });

    /* auto-search on category selection if search bar has input */
    $(".page-scroll").click(function() {
        if(this.id == "article-link") requestArticles("article");
        if(this.id == "world-link") requestArticles("world");
        if(this.id == "us-link") requestArticles("us");
        if(this.id == "politics-link") requestArticles("politics");
        if(this.id == "business-link") requestArticles("business");
        if(this.id == "science-link") requestArticles("science");
        if(this.id == "sports-link") requestArticles("sports");
    });

    /* retrieve current active search pane */
    function getActive() {
        if($('li.nav-top').hasClass('active') == true)
            return "top";
        if($('li.nav-article').hasClass('active') == true)
            return "article";
        if($('li.nav-world').hasClass('active') == true)
            return "world";
        if($('li.nav-us').hasClass('active') == true)
            return "us";
        if($('li.nav-politics').hasClass('active') == true)
            return "politics";
        if($('li.nav-business').hasClass('active') == true)
            return "business";
        if($('li.nav-science').hasClass('active') == true)
            return "science";
        if($('li.nav-sports').hasClass('active') == true)
            return "sports";
        if($('li.nav-movies').hasClass('active') == true)
            return "movies";
    }

    /* select api request based on active search pane */
    function requestSearch() {
        if(getActive() == "top") {
            /* show error if user inputs in search on top of page */
            if($.trim($("#search").val()) == "") return;
            $("#error").popover('show');
        }
        if(getActive() == "article") {
            $("#error").popover('hide');
            $("body").scrollTo("#article",{duration:'slow'});
            requestArticles("article");
        }
        if(getActive() == "world") {
            $("#error").popover('hide');
            $("body").scrollTo("#world",{duration:'slow'});
            requestArticles("world");
        }
        if(getActive() == "us") {
            $("#error").popover('hide');
            $("body").scrollTo("#us",{duration:'slow'});
            requestArticles("us");
        }
        if(getActive() == "politics") {
            $("#error").popover('hide');
            $("body").scrollTo("#politics",{duration:'slow'});
            requestArticles("politics");
        }
        if(getActive() == "business") {
            $("#error").popover('hide');
            $("body").scrollTo("#business",{duration:'slow'});
            requestArticles("business");
        }
        if(getActive() == "science") {
            $("#error").popover('hide');
            $("body").scrollTo("#science",{duration:'slow'});
            requestArticles("science");
        }
        if(getActive() == "sports") {
            $("#error").popover('hide');
            $("body").scrollTo("#sports",{duration:'slow'});
            requestArticles("sports");
        }
        if(getActive() == "movies") {
            $("#error").popover('hide');
            $("body").scrollTo("#movies",{duration:'slow'});
            requestMovies();
        }
    }

    /* dismiss popover on nav selection */
    $(".dismiss-popover").click(function() {
        $("#error").popover('hide');
    });

    /* submit search request on button press */
    $("#request-search").click(function() {
        requestSearch();
    });

    /* support for pressing enter to search */
    $("#search").keyup(function(event) {
        if(event.keyCode == 13) $("#request-search").click();
    });

    /* sanitize user input */
    function formatInput(string) {
        string = string.toLowerCase(); //convert to consistent lower case format
        string = string.replace(/ /g, "+"); //for multi-word search replace spaces with '+'
        return string;
    }

    /* ajax article search request to flask server */
    function requestArticles(filter) {
        var query = $.trim($("#search").val());
        if(query == "") return; //return if empty search string
        loading();
        query = formatInput(query);
        var id = "#" + filter; //id tag for given search filter
        $.ajax({
            type: "GET",
            url: "../search/api/v1.0/" + filter + "/" + query,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data, status, jqXHR) {
                $(id + "-header").hide();
                /* check if returned json is empty */
                if($.isEmptyObject(data)) {
                    $(id + "-results").hide();
                    $(id + "-header").html("No results found");
                    $(id + "-header").show();
                }
                else {
                    /* reset content */
                    $(id + "-indicators").html("");
                    $(id + "-content").html("");
                    var i, headline, url, date, snippet, image, byline;
                    for(i = 0; i < Object.keys(data).length; i++) {
                        /* retrieve content from json */
                        headline = data[i].headline;
                        byline = data[i].author;
                        url = data[i].url;
                        date = data[i].date;
                        if(date != null) {
                            date = date.split("T"); //simple split hack for date format
                            date = date[0]; //reassign first element of split array
                        }
                        snippet = data[i].snippet;
                        image = data[i].img;

                        /* dynamically insert carousel indicators */
                        if(i == 0) innerHTML = "<li data-target=\"#carousel-" + filter + "\" data-slide-to=\"0\" class=\"active\"></li>";
                        else innerHTML = "<li data-target=\"#carousel-" + filter + "\" data-slide-to=\"" + i + "\"></li>";
                        $(id + "-indicators").append(innerHTML);

                        /* dynamically insert content into carousel */
                        var innerHTML;
                        if(i == 0) innerHTML = "<div class=\"item active\">";
                        else innerHTML = "<div class=\"item\">";
                        innerHTML = innerHTML + "<div class=\"row\">";
                        innerHTML = innerHTML + "<div class=\"col-xs-6\">";
                        /* apply mod to alternate content layout */
                        if(i % 3 == 0) {
                            innerHTML = innerHTML + "<div class=\"well\">";
                            innerHTML = innerHTML + "<a class=\"page-scroll headline\" href=\"" + url + "\" target=\"_blank\"><h3>" + headline + "</h3></a>";
                            innerHTML = innerHTML + "<p>" + date + "</br>";
                            innerHTML = innerHTML + "<strong>" + byline + "</strong><br>" + snippet + "</p></div></div>";
                            innerHTML = innerHTML + "<div class=\"col-xs-6\">";
                            innerHTML = innerHTML + "<div class=\"slider-size\">";
                            innerHTML = innerHTML + "<img src=\"" + image + "\" class=\"img-thumbnail\"></div></div>";
                        }
                        else {
                            innerHTML = innerHTML + "<div class=\"slider-size\">";
                            innerHTML = innerHTML + "<img src=\"" + image + "\" class=\"img-thumbnail\"></div></div>";
                            innerHTML = innerHTML + "<div class=\"col-xs-6\">";
                            innerHTML = innerHTML + "<div class=\"well\">";
                            innerHTML = innerHTML + "<a class=\"page-scroll headline\" href=\"" + url + "\" target=\"_blank\"><h3>" + headline + "</h3></a>";
                            innerHTML = innerHTML + "<p>" + date + "</br>";
                            innerHTML = innerHTML + "<strong>" + byline + "</strong><br>" + snippet + "</p></div></div>";
                        }
                        innerHTML = innerHTML + "</div>";
                        $(id + "-content").append(innerHTML);
                    }
                    /* show results */
                    $(id + "-results").show();
                }
                /* mobile support -- auto collapse nav after search */
                $('.navbar-collapse').collapse('hide');
                loadingComplete();
            },
            error: function(jqXHR, status) {
                /* mobile support -- auto collapse nav after search */
                $('.navbar-collapse').collapse('hide');
                loadingComplete();
            },
            statusCode: {
                500: function() {
                    /* mobile support -- auto collapse nav after search */
                    $('.navbar-collapse').collapse('hide');
                    $(id + "-results").hide();
                    $(id + "-header").html("<strong>500 Error</strong>: Request to NYTimes API Timed Out<br>Please try again.");
                    $(id + "-header").show();
                    loadingComplete();
                }
            }
        });
    }
});