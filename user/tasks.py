from celery import shared_task

from social_network.models import Post
from user.models import User


@shared_task
def create_post(user_id: int) -> int:
    user = User.objects.get(id=user_id)
    title = "Test Celery Posts Creation"
    text = f"New post from user: {user.username}"
    Post.objects.create(user=user, title=title, text=text)
    return Post.objects.count()
