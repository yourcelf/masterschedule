import pytz
import time
import calendar
import datetime
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

register = template.Library()

tz = pytz.timezone(settings.TIME_ZONE)

def _time_steps(chunk, td, formatter, base):
    start = chunk["start"]
    end = chunk["end"]

    step = base
    steps = []
    while step < end:
        local_start = max(start, step)
        steps.append(
            [local_start, min(step + td, end),
                tz.normalize(local_start).strftime(formatter).lstrip("0")]
        )
        step += td

    return steps

@register.filter
def chunk_days(chunk):
    start = chunk['start']
    local = tz.normalize(start);
    base = datetime.datetime(local.year, local.month, local.day, tzinfo=local.tzinfo)
    return _time_steps(chunk, datetime.timedelta(days=1), u"%a %b %d", base)

@register.filter
def chunk_hours(chunk):
    start = chunk['start']
    base = datetime.datetime(start.year, start.month, start.day, start.hour, tzinfo=start.tzinfo)
    return _time_steps(chunk, datetime.timedelta(hours=1), u"%I:%M%P", base)

@register.filter
def timestamp(date):
    return calendar.timegm(date.utctimetuple())

def admin_edit_link(model, tab=""):
    url = reverse('admin:{}_{}_change'.format(
        model._meta.app_label, model._meta.model_name
    ), args=[model.pk])
    return u"<a class='admin-edit-link' target='_blank' href='{url}{extra}' " \
           u"title='Edit {type} {name}'>" \
           u"&#9998; Edit {type} {short_name}{tab}</a>".format(
                   url=url,
                   extra="#tab_%s" % tab if tab else "",
                   tab=" (%s)" % tab if tab else "",
                   type=model._meta.verbose_name,
                   name=unicode(model),
                   short_name=truncatechars(unicode(model), 30))


@register.simple_tag(takes_context=True)
def open_admin_edit_region(context, model, tab=""):
    user = context['user']
    editable = (
        hasattr(model, "_meta") and
        user.has_perm("{}.change_{}".format(model._meta.app_label, model._meta.model_name))
    )
    if editable: 
        html = u"".join((
            "<div class='edit-region editable'>",
            admin_edit_link(model, tab)
        ))
    else:
        html = "<div class='edit-region'>"
    return mark_safe(html)

@register.simple_tag
def close_admin_edit_region():
    return "</div>"

@register.filter
def message_alert_class(tags):
    return {
        "success": "alert alert-success",
        "warning": "alert alert-warning",
        "error": "alert alert-danger",
    }.get(tags, "alert alert-info")
