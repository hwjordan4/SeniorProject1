function adjustStyle(width) {
    width = parseInt(width);
    if (width < 600) {
        $(".sidebar").css("position", "relative");
    } else {
        $(".sidebar").css("position", "fixed");
    }
}

$(function () {
    adjustStyle($(this).width());
    $(window).resize(function () {
        adjustStyle($(this).width());
    });
});

$(document).ready(function () {
    $('.collapsible').collapsible({
        accordion: false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
    });
});
