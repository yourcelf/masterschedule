function showAddRoleForm(event) {
  event.preventDefault();
  var url = $(event.currentTarget).attr("data-available-people-url");
  var parent = $(event.currentTarget).closest("table.roles");
  if (parent.find(".person-holder").length > 0) {
    $.get(url, function(data) {
      var select = $("<select name='person'></select>");
      select.append($("<option value=''></option>"));
      for (var i = 0; i < data.length; i++) {
        select.append($("<option value='" + data[i].value + "'>" + data[i].name + "</option>"));
      }
      parent.find(".person-holder").replaceWith(select);
    });
  }
  parent.find(".add-button").hide();
  parent.find(".add-form").removeClass("hide");
}
function deleteRole(event) {
  event.preventDefault();
  var $el = $(event.currentTarget);
  $.post($(event.currentTarget).attr("href"), function(data) {
    updateRow($(event.currentTarget).closest(".event-role-row"), data);
  });
}
function addRole(event) {
  var form = $(event.currentTarget);
  event.preventDefault();
  var url = form.attr("action");
  var data = {
    person: form.find("[name=person]").val(),
    role: form.find("[name=role]").val()
  };
  if (data.role == "") {
    alert("Please add a role.");
    return;
  }

  $.post(url, data, function(data) {
    updateRow(form.closest(".event-role-row"), data);
  });
}
function cancelForm(event) {
  event.preventDefault();
  var parent = $(event.currentTarget).closest("table.roles");
  parent.find(".add-button").show();
  parent.find(".add-form").addClass("hide");
}

function registerHandlers(parent) {
  $("a.add-role", parent).click(showAddRoleForm);
  $("a.delete-role", parent).click(deleteRole);
  $("form.add-role", parent).submit(addRole);
  $("a.cancel-add-role", parent).click(cancelForm);
}

function updateRow(selector, data) {
    var $data = $(data);
    registerHandlers($data);
    selector.replaceWith($data);
}

registerHandlers(document);
