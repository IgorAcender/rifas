# Generated migration to fix duplicate premium_numbers column issue

from django.db import migrations


def fix_duplicate_premium_numbers(apps, schema_editor):
    """Remove duplicate premium_numbers column if it exists due to migration errors"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            # Check if the column exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name='raffles_raffle' AND column_name='premium_numbers';
            """)
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                # Column exists, just ensure it's nullable
                try:
                    cursor.execute("""
                        ALTER TABLE raffles_raffle
                        ALTER COLUMN premium_numbers DROP NOT NULL;
                    """)
                except Exception:
                    # Column might already be nullable, ignore
                    pass


def reverse_fix(apps, schema_editor):
    """Reverse operation - do nothing"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('raffles', '0016_add_home_redirect_raffle'),
    ]

    operations = [
        migrations.RunPython(
            fix_duplicate_premium_numbers,
            reverse_fix
        ),
    ]
