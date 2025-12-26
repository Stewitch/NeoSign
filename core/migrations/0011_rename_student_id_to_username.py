from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_add_username_display_settings'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='student_id',
            new_name='username',
        ),
    ]
