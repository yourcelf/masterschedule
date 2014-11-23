from django.conf.urls import patterns, include, url

from schedule.views import (
        # Public
        ConferenceCreate, ConferenceList, MasterSchedule, PersonalSchedule,
        RoomSchedule, PrintAll, AirportDesires,
        
        # Permission required
        PersonCrud, VenueCrud, RoleTypeCrud, EventAssigner, ConferenceUpdate,

        # Secret URL
        AvailabilitySurvey,

        # Ajax
        EventRoleAjaxCrud, update_event_attribute,
        # Ajax: permission required
        get_available_people, get_available_venues, get_admin_data
    )

urlpatterns = patterns('',
    url(r'^$', ConferenceList.as_view(), name='conferences'),
    url(r'^admin-data$', get_admin_data, name='get_admin_data'),
    url(r'^schedule/(?P<slug>[^/]+)/$', MasterSchedule.as_view(), name='master_schedule'),
    url(r'^assign/(?P<slug>[^/]+)/$', EventAssigner.as_view(), name='event_assigner'),
    url(r'^venues/(?P<slug>[^/]+)/$', VenueCrud.as_view(), name='venue_crud'),
    url(r'^people/(?P<slug>[^/]+)/$', PersonCrud.as_view(), name='person_crud'),
    url(r'^roletypes/(?P<slug>[^/]+)/$', RoleTypeCrud.as_view(), name='roletype_crud'),
    url(r'^airport/(?P<slug>[^/]+)/$', AirportDesires.as_view(), name='airport_list'),
    url(r'^printall/(?P<slug>[^/]+)/$', PrintAll.as_view(), name='print_all'),
    url(r'^survey/(?P<slug>[^/]+)/$', AvailabilitySurvey.as_view(), name='availability_survey'),
    url(r'^personal/(?P<slug>[^/]+)/(?P<pk>\d+)/$', PersonalSchedule.as_view(), name='personal_schedule'),
    url(r'^room/(?P<slug>[^/]+)/$', RoomSchedule.as_view(), name='venue_schedule'),
    url(r'^create-conference/', ConferenceCreate.as_view(), name='conference_create'),
    url(r'^update-conference/(?P<slug>[^/]+)/$', ConferenceUpdate.as_view(),
        name='conference_update'),

    # AJAX methods for altering events.
    url(r'^event/edit-role/', EventRoleAjaxCrud.as_view(), name='event_role_crud'),
    url(r'^event/available-people/', get_available_people, name='get_available_people'),
    url(r'^event/update-event-attribute/', update_event_attribute, name='update_event_attribute'),
    url(r'^event/available-venues/', get_available_venues, name='get_available_venues'),
)
