var pixelsPerDay = 4000;
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
      height: $el.outerHeight(true),
      top: 0,
      bottom: 0
    };

    var possibleTops = [0];
    var hoverlaps = [];
    var other;
    for (var j = 0; j < ystack[key].length; j++) {
      other = ystack[key][j];
      if (atts.end > other.start && atts.start < other.end) {
        possibleTops.push(other.bottom);
        hoverlaps.push(other);
      }
    }
    var top,bottom,found;
    for (var k = 0; k < possibleTops.length; k++) {
      top = possibleTops[k];
      bottom = top + atts.height;
      found = true;
      for (var h = 0; h < hoverlaps.length; h++) {
        other = hoverlaps[h];
        if (other.top < bottom && other.bottom > top) {
          found = false;
          break;
        }
      }
      if (found) {
        break;
      }
    }
    atts.top = top;
    atts.bottom = bottom;
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
  $(".time-block,.hour-block,.day-block").each(setWidth);
  $(".time-block,.hour-block,.day-block").each(setX);
  $(".chunk").each(function(i, el) {
    var height = setY("events-" + i, $(el).find(".events .time-block"));
    $(el).height($(el).height() + height);
  });
  var scrollTimeout;
  $(".timeheader").each(function(i, el) {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    setTimeout(function() {
      var $el = $(el);
      var left = $el.offset().left;
      var chunk = $el.closest(".chunk");
      var chunkTop = chunk.offset().top;
      var chunkBottom = chunkTop + chunk.height();
      $(window).scroll(function() {
        var css;
        var scrollTop = $(window).scrollTop();
        if (scrollTop > chunkTop && scrollTop < chunkBottom) {
           $el.addClass("affix");
           css = {"top": (scrollTop - chunkTop) + "px"};
        } else {
           $el.removeClass("affix");
           css = {"top": "auto"};
        }
        $el.css(css);
      });
    }, 100);
  });
});
