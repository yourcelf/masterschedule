import os
import json
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

from django.db.models import Q, F, Max, Avg, Count
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.core.urlresolvers import reverse

#from django.contrib.sites.models import *
#site = Site.objects.get_current()
from django.contrib.auth.models import Group, User

from schedule.models import *
