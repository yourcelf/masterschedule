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
var yoffset = 21;
var ystack = {};
function setY(key, els) {
  if (!ystack[key]) {
    ystack[key] = [];
  }
  var maxHeight = 0;
  els.each(function(i, el) {
    var $el = $(el);
    var start = parseInt($el.attr("data-start-time"));
    var end = parseInt($el.attr("data-end-time"));
    var count = 0;
    var other;
    for (var j = 0; j < ystack[key].length; j++) {
      other = ystack[key][j];
      if (other[0] <= end && other[1] > start) {
        count += 1;
      }
    }
    ystack[key].push([start, end]);
    $el.css("top", (yoffset * count) + "px");
    maxHeight = Math.max(count, maxHeight);
  });
  return (maxHeight + 1) * yoffset;
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
