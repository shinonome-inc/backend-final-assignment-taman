# Generated by Django 4.1.9 on 2023-06-27 11:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tweets", "0002_like"),
    ]

    operations = [
        migrations.AlterField(
            model_name="like",
            name="target",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="liked_tweet", to="tweets.tweet"
            ),
        ),
        migrations.AlterField(
            model_name="like",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="liked_user", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(fields=("target", "user"), name="like_unique"),
        ),
    ]
