from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as DjangoUser
from apps.graph.models import User as Neo4jUser

@receiver(post_save, sender=DjangoUser)
def create_neo4j_user(sender, instance, created, **kwargs):
    if created:
        # Check if the Neo4j user already exists to prevent duplicate errors
        if not Neo4jUser.nodes.get_or_none(username=instance.username):
            Neo4jUser(
                username=instance.username,
                email=instance.email or '',
            ).save()
