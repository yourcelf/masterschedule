from django.db import models
from django.core.urlresolvers import reverse

class Conference(models.Model):
    name = models.CharField(max_length=70)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def get_absolute_url(self):
        return reverse("master_schedule", kwargs={"pk": self.pk})

    def __unicode__(self):
        return self.name

class Person(models.Model):
    conference = models.ForeignKey(Conference)
    name = models.CharField(max_length=70)
    availability_start_date = models.DateTimeField(blank=True, null=True)
    availability_end_date = models.DateTimeField(blank=True, null=True)
    want_airport_pickup = models.BooleanField(default=False)
    airport_pickup_details = models.TextField(blank=True)
    want_airport_dropoff = models.BooleanField(default=False)
    airport_dropoff_details = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class OtherCommitment(models.Model):
    person = models.ForeignKey(Person)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.person)

class Period(models.Model):
    conference = models.ForeignKey(Conference)
    period = models.CharField(max_length=70)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __unicode__(self):
        return self.period

class Venue(models.Model):
    conference = models.ForeignKey(Conference)
    name = models.CharField(max_length=70)

    def __unicode__(self):
        return self.name

class EventType(models.Model):
    conference = models.ForeignKey(Conference)
    type = models.CharField(max_length=70)

    def __unicode__(self):
        return "{}: {}".format(self.conference, self.type)

class Event(models.Model):
    conference = models.ForeignKey(Conference)
    title = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    period = models.ForeignKey(Period, blank=True, null=True,
            help_text="If set, will override start and end dates.")

    type = models.ForeignKey(EventType, blank=True, null=True)

    description = models.TextField(blank=True)
    url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.period:
            self.start_date = self.period.start_date
            self.end_date = self.period.end_date
        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

class RoleType(models.Model):
    conference = models.ForeignKey(Conference)
    role = models.CharField(max_length=70)

    def __unicode__(self):
        return self.role

class EventRole(models.Model):
    event = models.ForeignKey(Event)
    role = models.ForeignKey(RoleType, blank=True, null=True)
    person = models.ForeignKey(Person, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.role)
