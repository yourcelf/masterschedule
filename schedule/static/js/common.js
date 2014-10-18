$("[data-toggle='tooltip']").tooltip();
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$("[data-role='date-time-widget']").each(function(i, el) {
  var parent = $(el);
  var dest = parent.find("[data-role='date-time']");
  var dateEl = parent.find("[data-role='date']");
  var hoursEl = parent.find("[data-role='hours']");
  var minutesEl = parent.find("[data-role='minutes']");
  var ampmEl = parent.find("[data-role='ampm']");
  new Pikaday({ field: dateEl[0], format: "YYYY-MM-DD" });
  parent.find("[type='date'], select").change(function() {
    console.log("CHANGEO");
    var date = dateEl.val();
    if (date) {
      var hours = parseInt(hoursEl.val(), 10)
      var minutes = parseInt(minutesEl.val(), 10)
      var pm = ampmEl.val() === "pm";
      if (!pm && hours === 12) {
        hours = 0;
      } else if (pm && hours !== 12) {
        hours += 12;
      }
      dest.val(
        date + " " +
        (hours < 10 ? "0" : "") + hours + ":" +
        (minutes < 10 ? "0" : "") + minutes + ":00"
      );
    } else {
      dest.val("");
    }
  });
});

// Highlight effect
var notLocked = true;
$.fn.animateHighlight = function(highlightColor, duration) {
    var highlightBg = highlightColor || "#FFFF9C";
    var animateMs = duration || 1500;
    var originalBg = this.css("backgroundColor");
    if (notLocked) {
        notLocked = false;
        this.stop().css("background-color", highlightBg)
            .animate({backgroundColor: originalBg}, animateMs);
        setTimeout( function() { notLocked = true; }, animateMs);
    }
};
