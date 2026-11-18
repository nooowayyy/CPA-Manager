from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .defaults import DEFAULT_PLATFORMS, DEFAULT_CHANNELS
from .models import Platform, Channel


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_dimensions(sender, instance, created, **kwargs):
    if not created:
        return
    for code, name in DEFAULT_PLATFORMS:
        Platform.objects.get_or_create(user=instance, code=code, defaults={"name": name})
    for code, name in DEFAULT_CHANNELS:
        Channel.objects.get_or_create(user=instance, code=code, defaults={"name": name})
