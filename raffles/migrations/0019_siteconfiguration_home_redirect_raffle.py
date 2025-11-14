# Generated migration - Skip duplicate home_redirect_raffle field
# The field already exists in the database, this migration just marks it as processed

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0018_raffle_milestone_prize_file_and_more'),
    ]

    operations = [
        # This migration is intentionally empty
        # The home_redirect_raffle field already exists in the database
        # from a previous migration or manual creation
    ]
