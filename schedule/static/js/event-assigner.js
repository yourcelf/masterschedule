function showAddRoleForm(event, formdata) {
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
      if (formdata && formdata.personId) {
        select.val(formdata.personId);
      }
    });
  } else {
      if (formdata && formdata.personId) {
        $("[name=person]").val(formdata.personId);
      }
  }
  parent.find(".add-button").hide();
  parent.find(".add-form").removeClass("hide");
  if (formdata) {
    parent.find("[name=role]").val(formdata.roleTypeId);
    parent.find("[name=id]").val(formdata.id);
    parent.find("[type=submit]").html("Update");
  } else {
    parent.find("[type=submit]").html("Add");
  }
}
function deleteRole(event) {
  event.preventDefault();
  var $el = $(event.currentTarget);
  $.post($(event.currentTarget).attr("href"), function(data) {
    updateRow($(event.currentTarget).closest(".event-role-row"), data);
  });
}
function editRole(event) {
  event.preventDefault();
  var $el = $(event.currentTarget);
  var data = {
    id: $el.attr("data-role-id"),
    roleTypeId: $el.attr("data-roletype-id"),
    personId: $el.attr("data-person-id")
  };
  showAddRoleForm(event, data);
}
function addRole(event) {
  var form = $(event.currentTarget);
  event.preventDefault();
  var url = form.attr("action");
  var data = {
    person: form.find("[name=person]").val(),
    role: form.find("[name=role]").val()
  };
  var id = form.find("[name=id]").val();
  if (id) {
    data.id = id;
  }
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
function updateEventAttribute(jqevt) {
  jqevt.preventDefault();
  var $el = $(jqevt.currentTarget);
  var url = $el.attr("data-url");
  var data = {
    name: $el.attr("name"),
    value: $el.val(),
  };
  $.post(url, data, function(data) {
    updateRow($el.closest(".event-role-row"), data);
  });
}

function registerHandlers(parent) {
  $("a.add-role", parent).click(showAddRoleForm);
  $("a.delete-role", parent).click(deleteRole);
  $("form.add-role", parent).submit(addRole);
  $("a.cancel-add-role", parent).click(cancelForm);
  $("[data-action='update-event-attribute']", parent).change(updateEventAttribute);
  $(".edit-role", parent).click(editRole);
}


function updateRow(selector, data) {
    var $data = $(data);
    registerHandlers($data);
    selector.replaceWith($data);
}

registerHandlers(document);
