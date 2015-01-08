import re
from django.test import TestCase, Client
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from schedule.models import Conference, Person

class TestCreateConference(TestCase):
    def test_sign_up_to_event_creation(self):
        self.assertFalse(User.objects.filter(username="test").exists())

        c = Client()
        res = c.get(reverse("registration_register"))
        self.assertEquals(res.status_code, 200)
        res = c.post(reverse("registration_register"), {
            "username": "test",
            "email": "test@example.com",
            "password1": "password",
            "password2": "password"
        })
        self.assertRedirects(res, reverse("registration_complete"), status_code=302,
                target_status_code=200)
        self.assertTemplateUsed(res, "registration/activation_email.html")
        self.assertTemplateUsed(res, "registration/activation_email.txt")
        self.assertTemplateUsed(res, "registration/activation_email_subject.txt")

        self.assertEquals(len(mail.outbox), 1)
        match = re.search("(https://example.com/accounts/activate/\w+/)", mail.outbox[0].body)
        self.assertTrue(bool(match))

        activation_url = match.group(1).replace("https://example.com", "")
        res = c.get(activation_url)
        self.assertRedirects(res, reverse("registration_activation_complete"),
                status_code=302, target_status_code=200)

        self.assertTrue(User.objects.filter(username="test").exists())

        res = c.get(reverse("auth_login"))
        self.assertEquals(res.status_code, 200)
        res = c.post(reverse("auth_login"), {
            "username": "test",
            "password": "password"
        }, follow=True)
        self.assertEquals(res.redirect_chain, [
            ("http://testserver/accounts/profile/", 302),
            ("http://testserver{}".format(reverse("conferences")), 302),
        ])

        res = c.get("/")
        self.assertTemplateUsed(res, "schedule/conference_list.html")
        self.assertContains(res, "Create a New Master Schedule")

        
        res = c.get(reverse("conference_create"))
        self.assertEquals(res.status_code, 200)

class TestAvailabilityPrefs(TestCase):
    def test_add_availability_prefs(self):
        conference = Conference.objects.create(name="Test Conference", public=False)
        person = Person.objects.create(name="Charlie", conference=conference)

        c = Client()
        url = reverse("availability_survey", args=[person.random_slug]).replace("%3D", "=")
        res = c.get(url)
        self.assertContains(res, "Charlie availability")
        res = c.post(url, {
            "name": "Charlie",
            "attending": True,
            "availability_start_date": "2015-01-08 08:00:00",
            "availability_end_date": "2015-01-09 08:00:00",
            "othercommitment_set-TOTAL_FORMS": "2",
            "othercommitment_set-INITIAL_FORMS": "0",
            "othercommitment_set-MIN_NUM_FORMS": "0",
            "othercommitment_set-MAX_NUM_FORMS": "1000",
        })
        self.assertRedirects(res, url)
