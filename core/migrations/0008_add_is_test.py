from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_map_security_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_test',
            field=models.BooleanField(default=False, verbose_name='测试账号'),
        ),
    ]
