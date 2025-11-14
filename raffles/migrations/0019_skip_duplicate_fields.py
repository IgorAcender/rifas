# Generated migration - Skip duplicate fields
# These fields already exist in the database

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0018_raffle_milestone_prize_file_and_more'),
    ]

    operations = [
        # This migration is intentionally empty
        # The following fields already exist in the database:
        # - raffle.premium_numbers
        # - siteconfiguration.home_redirect_raffle
        # - siteconfiguration.admin_phones (altered)
        # - siteconfiguration.group_phones (altered)
        # This migration just marks them as processed
    ]
