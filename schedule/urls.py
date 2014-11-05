from django.conf.urls import patterns, include, url

from schedule.views import (
        MasterSchedule, PersonalSchedule, RoomSchedule, PrintAll,
        ConferenceList, EventAssigner, PersonList,  VenueList, AirportDesires,
        AvailabilitySurvey, add_event_role, remove_event_role,
        get_available_people, update_event_attribute, get_available_venues
    )

urlpatterns = patterns('',
    url(r'^$', ConferenceList.as_view(), name='conferences'),
    url(r'^(?P<pk>\d+)/$', MasterSchedule.as_view(), name='master_schedule'),
    url(r'^(?P<pk>\d+)/events/$', EventAssigner.as_view(), name='event_assigner'),
    url(r'^(?P<pk>\d+)/venues/$', VenueList.as_view(), name='venue_list'),
    url(r'^(?P<pk>\d+)/survey/$', PersonList.as_view(), name='person_list'),
    url(r'^(?P<pk>\d+)/airport/$', AirportDesires.as_view(), name='airport_list'),
    url(r'^(?P<pk>\d+)/printall/$', PrintAll.as_view(), name='print_all'),
    url(r'^survey/(?P<pk>\d+)/$', AvailabilitySurvey.as_view(), name='availability_survey'),
    url(r'^my/(?P<slug>.*)/$', PersonalSchedule.as_view(), name='personal_schedule'),
    url(r'^room/(?P<pk>\d+)/$', RoomSchedule.as_view(), name='venue_schedule'),

    # AJAX methods for altering events.
    url(r'^event/add-role/', add_event_role, name='add_event_role'),
    url(r'^event/remove-role/', remove_event_role, name='remove_event_role'),
    url(r'^event/available-people', get_available_people, name='get_available_people'),
    url(r'^event/update-event-attribute', update_event_attribute, name='update_event_attribute'),
    url(r'^event/available-venues', get_available_venues, name='get_available_venues'),

)
