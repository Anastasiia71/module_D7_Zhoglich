from celery import shared_task
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string
from .models import *
import time
from datetime import datetime


@shared_task
def send_notifications(preview, pk, title, subscribers):
    html_contest = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/news/{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_contest, 'text/html')
    msg.send()


@shared_task
@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        subscribers: list[str] = []
        for category in categories:
            subscribers += category.subscribers.all()

        subscribers = [s.email for s in subscribers]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers)


@shared_task
def notify_weekly():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(added_at__gte=last_week)
    categories = set(posts.values_list('postCategory__name', flat=True))
    subscribers = Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True)
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()