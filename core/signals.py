from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile,Video
from .search.document import VideoDocument

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Video)
def index_video(sender, instance, **kwargs):
    VideoDocument().update(instance)

@receiver(post_delete, sender=Video)
def delete_video(sender, instance, **kwargs):
    VideoDocument().delete(instance)
