from django.contrib import admin

from schedule.models import *

# Register your models here.
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']
admin.site.register(Conference, ConferenceAdmin)

class OtherCommitmentInline(admin.TabularInline):
    model = OtherCommitment

class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'conference', 'availability_start_date', 'availability_end_date']
    list_filter = ['conference']
    inlines = [OtherCommitmentInline]
admin.site.register(Person, PersonAdmin)

class PeriodAdmin(admin.ModelAdmin):
    list_display = ['period', 'conference', 'start_date', 'end_date']
    list_filter = ['conference']
admin.site.register(Period, PeriodAdmin)


class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'conference']
    list_filter = ['conference']
admin.site.register(Venue, VenueAdmin)

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'conference']
    list_filter = ['conference']
admin.site.register(EventType, EventTypeAdmin)

class RoleTypeAdmin(admin.ModelAdmin):
    list_display = ['role', 'conference']
    list_filter = ['conference']
admin.site.register(RoleType, RoleTypeAdmin)

class EventRoleInline(admin.TabularInline):
    model = EventRole
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(EventRoleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in ("person", "role"):
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(conference=request._obj_.conference)
            else:
                field.queryset = field.queryset.none()
        return field

class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'period', 'start_date', 'end_date']
    list_filter = ['conference', 'type']
    inlines = [EventRoleInline]
    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(EventAdmin, self).get_form(request, obj, **kwargs)
admin.site.register(Event, EventAdmin)

