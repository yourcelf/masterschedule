from django.conf.urls import patterns, include, url

from schedule.views import (
        MasterSchedule, PersonalSchedule, ConferenceList,
        EventAssigner, PersonList,  AvailabilitySurvey,
        add_event_role, remove_event_role, get_available_people,
        update_event_attribute
    )

urlpatterns = patterns('',
    url(r'^$', ConferenceList.as_view(), name='conferences'),
    url(r'^(?P<pk>\d+)/$', MasterSchedule.as_view(), name='master_schedule'),
    url(r'^(?P<pk>\d+)/events/$', EventAssigner.as_view(), name='event_assigner'),
    url(r'^(?P<pk>\d+)/survey/$', PersonList.as_view(), name='person_list'),
    url(r'^survey/(?P<pk>\d+)/$', AvailabilitySurvey.as_view(), name='availability_survey'),
    url(r'^my/(?P<pk>\d+)/$', PersonalSchedule.as_view(), name='personal_schedule'),
    url(r'^event/(?P<pk>\d+)/add-role/', add_event_role, name='add_event_role'),
    url(r'^event/(?P<pk>\d+)/remove-role/', remove_event_role, name='remove_event_role'),
    url(r'^event/(?P<pk>\d+)/available-people', get_available_people, name='get_available_people'),
    url(r'^event/(?P<pk>\d+)/update-event-attribute', update_event_attribute, name='update_event_attribute'),

)
