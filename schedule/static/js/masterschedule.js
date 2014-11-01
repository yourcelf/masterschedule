var pixelsPerDay = 2500;
var secondsPerDay = 60 * 60 * 24;

function setWidth(i, el) {
  var $el = $(el);
  var start = parseInt($el.attr("data-start-time"));
  var end = parseInt($el.attr("data-end-time"));
  $el.width(pixelsPerDay * (end - start) / secondsPerDay);
}
function setX(i, el) {
  var $el = $(el);
  var parent = $el.closest(".chunk");
  var elStart = parseInt($el.attr("data-start-time"));
  var parentStart = parseInt(parent.attr("data-start-time"));
  var parentEnd = parseInt(parent.attr("data-end-time"));
  $el.css("left",
      (100 * ((elStart - parentStart) / (parentEnd - parentStart))) + "%"
   );
}

var ystack = {};
function setY(key, els) {
  if (!ystack[key]) {
    ystack[key] = [];
  }
  
  var maxBottom = 0;
  els.each(function(i, el) {
    var $el = $(el);
    var atts = {
      start: parseInt($el.attr("data-start-time")),
      end: parseInt($el.attr("data-end-time")),
      top: 0,
      bottom: 0
    };

    var other;
    for (var j = 0; j < ystack[key].length; j++) {
      other = ystack[key][j];
      console.log(other);
      if (atts.end >= other.start && atts.start < other.end) {
        atts.top = Math.max(atts.top, other.bottom);
      }
    }

    atts.bottom = atts.top + $el.outerHeight(true);
    ystack[key].push(atts);
    $el.css("top", atts.top + "px");
    maxBottom = Math.max(maxBottom, atts.bottom);
  });
  return maxBottom;
}

$(document).ready(function() {
  $(".chunk").each(setWidth);
  var total = 0;
  $(".chunk").each(function() {
    total = Math.max(total, $(this).outerWidth(true));
  });
  $(".ms").width(total);
  $(".time-block").each(setWidth);
  $(".time-block").each(setX);
  $(".chunk").each(function(i, el) {
    var height = setY("events-" + i, $(el).find(".events .time-block"));
    $(el).height($(el).height() + height);
  });
});
