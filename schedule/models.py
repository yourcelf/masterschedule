import os
import base64
import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

def random_slug():
    return base64.urlsafe_b64encode(os.urandom(32)).replace("=", "%3D")

class RandomSlugModel(models.Model):
    random_slug = models.CharField(max_length=64, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.random_slug:
            self.random_slug = random_slug()
        super(RandomSlugModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

class ConferenceManager(models.Manager):
    def public_for(self, user):
        q = Q(public=True)
        if user.is_authenticated():
            q = q | Q(admins__id=user.id)
        return self.active().filter(q).order_by('-created').distinct()

    def editable_by(self, user):
        return Conference.objects.filter(admins__id=user.id)

    def active(self):
        return self.filter(archived=False)

class ProspectiveAdmin(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    def __unicode__(self):
        return self.email

@receiver(post_save)
def convert_prospective_admins(sender, instance, created, raw, *args, **kwargs):
    if created and not raw and isinstance(instance, User) and instance.email:
        user = instance
        try:
            prospy = ProspectiveAdmin.objects.get(email=user.email)
        except ProspectiveAdmin.DoesNotExist:
            return
        for conference in prospy.conference_set.all():
            conference.admins.add(user)
            conference.prospective_admins.remove(prospy)
        prospy.delete()

class Conference(RandomSlugModel):
    name = models.CharField(max_length=70)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    public = models.BooleanField(default=True,
            help_text="List this conference on the front page? Uncheck for more privacy.")
    archived = models.BooleanField(default=False,
            help_text="Remove this conference from your list?")
    admins = models.ManyToManyField(User)
    prospective_admins = models.ManyToManyField(ProspectiveAdmin, null=True, blank=True)

    objects = ConferenceManager()

    def is_admin(self, user):
        return (user.is_superuser or self.admins.filter(pk=user.pk).exists())

    def get_absolute_url(self):
        return reverse("master_schedule", kwargs={"slug": self.random_slug})

    def __unicode__(self):
        return self.name

class Person(RandomSlugModel):
    conference = models.ForeignKey(Conference)
    name = models.CharField(max_length=70)
    attending = models.BooleanField(default=True,
            help_text="Are you attending?")
    availability_start_date = models.DateTimeField(blank=True, null=True,
            help_text="When are you first available to volunteer?")
    availability_end_date = models.DateTimeField(blank=True, null=True,
            help_text="When do you leave?")
    want_airport_pickup = models.BooleanField(default=False,
            help_text="Airport pickups might not be available.  But if we have capacity, would you like to get a ride?")
    airport_pickup_date = models.DateTimeField(blank=True, null=True,
            help_text="When do you arrive at the airport?")
    airport_pickup_details = models.TextField(blank=True,
            help_text="Please list your flight information.")
    want_airport_dropoff = models.BooleanField(default=False,
            help_text="Airport dropoffs might not be available.  But if we have capacity, would you like to get a ride?")
    airport_dropoff_date = models.DateTimeField(blank=True, null=True,
            help_text="When do you need to be at the airport? (e.g. one hour before flight departure)")
    airport_dropoff_details = models.TextField(blank=True,
            help_text="Please list your flight information.")

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

class Venue(RandomSlugModel):
    conference = models.ForeignKey(Conference)
    name = models.CharField(max_length=70)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ['conference', 'name']

class Event(models.Model):
    guid = models.CharField(max_length=36, unique=True)
    conference = models.ForeignKey(Conference)
    title = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    period = models.ForeignKey(Period, blank=True, null=True,
            help_text="If set, will override start and end dates.")

    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
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

    class Meta:
        ordering = ['role']

class EventRole(models.Model):
    event = models.ForeignKey(Event)
    role = models.ForeignKey(RoleType, blank=True, null=True)
    person = models.ForeignKey(Person, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.role)

    class Meta:
        ordering = ['role']

class RolePreference(models.Model):
    person = models.ForeignKey(Person)
    roletype = models.ForeignKey(RoleType)

    def __unicode__(self):
        return "{} => {}".format(self.person, self.roletype)
