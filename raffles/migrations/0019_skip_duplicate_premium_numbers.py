# Generated migration to skip the duplicate premium_numbers issue

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0018_raffle_milestone_prize_file_and_more'),
    ]

    operations = [
        # This migration is intentionally empty
        # It prevents the automatic migration from trying to add premium_numbers again
        # The column already exists in the database from earlier migrations
    ]
