function registerHandlers(parent) {
  $(".add-event-role, .edit-event-role", parent).click(showAddEventRoleForm);
  $(".remove-event-role", parent).click(removeEventRole);
  $("[data-action='update-event-attribute']", parent).change(updateEventAttribute);
}

var addFormModalTemplate = _.template($("#add-event-role-modal").html());
var personRowTemplate = _.template($("#person-select-row").html());

function showAddEventRoleForm(event) {
  event.preventDefault();
  var $el = $(event.currentTarget);
  var formData = {
    eventId: $el.attr("data-event-id"),
    eventRoleId: $el.attr("data-event-role-id"),
    roleTypeId: $el.attr("data-roletype-id"),
    personId: $el.attr("data-person-id")
  };
  formData.buttonLabel = formData.eventRoleId ? "Update" : "Add";

  var modal = $(addFormModalTemplate(formData));
  var personHolder = modal.find(".person-holder");
  var personUrl = personHolder.attr("data-url");

  // Update people list
  var personSelect = modal.find("[name=person]");
  modal.find("[name=role]").on("change", function(roleEvent) {
    var val = $(roleEvent.currentTarget).val();
    personSelect.select2("destroy");
    personSelect.hide();
    personHolder.addClass("loading");
    if (val) {
      var data = {
        roleTypeId: val,
        eventId: formData.eventId,
        eventRoleId: formData.eventRoleId
      };
      $.get(personUrl, data, function(res) {
        personHolder.removeClass("loading");
        personSelect.show();
        personSelect.select2({
          data: res,
          placeholder: "Choose person",
          formatSelection: personRowTemplate,
          formatResult: personRowTemplate,
          allowClear: true
        });
      });
    }
  }).change();

  var form = modal.find("form");
  form.on("submit", function(event) {
    event.preventDefault();
    var data = {
      person: form.find("[name=person]").val(),
      role: form.find("[name=role]").val(),
      eventRoleId: form.find("[name=eventrole_id]").val(),
      eventId: form.find("[name=event_id]").val()
    };
    if (!data.role) {
      alert("Please add a role.");
      return;
    };
    var url = form.attr("action");
    $.post(url, data, function(res) {
      updateRow($el.closest(".event-role-row"), res);
    });
    modal.modal('hide');
  });
  modal.find(".close, .closeme").on("click", function(event) {
    event.preventDefault();
    modal.modal('hide');
  });
  modal.on("hidden.bs.modal", function(e) {
    modal.remove();
  });
  $("body").append(modal);
  modal.modal('show');
}

function removeEventRole(event) {
  event.preventDefault();
  var $el = $(event.currentTarget);
  var data = {eventRoleId: $el.attr("data-event-role-id")}
  $.post($(event.currentTarget).attr("href"), data, function(res) {
    updateRow($(event.currentTarget).closest(".event-role-row"), res);
  });
}
function updateEventAttribute(jqevt) {
  jqevt.preventDefault();
  var $el = $(jqevt.currentTarget);
  var url = $el.attr("data-url");
  var data = {
    name: $el.attr("name"),
    value: $el.val(),
    eventId: $el.attr("data-event-id")
  };
  $.post(url, data, function(data) {
    updateRow($el.closest(".event-role-row"), data);
  });
}


function updateRow(selector, data) {
  var $data = $(data);
  registerHandlers($data);
  selector.replaceWith($data);
  $data.animateHighlight();
}

registerHandlers(document);
