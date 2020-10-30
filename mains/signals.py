from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from django.contrib.auth.models import User
import mains.models

# Defining signals
friendship_request_created = Signal()
friendship_request_declined = Signal()
friendship_request_accepted = Signal()
friendship_request_cancelled = Signal()


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         mains.models.Profile.objects.create(user=instance)