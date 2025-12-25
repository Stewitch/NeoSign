from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0002_activity_location_enabled_activity_location_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkinrecord',
            name='status',
            field=models.CharField(
                choices=[('present', '已签到'), ('manual', '手动签到'), ('excused', '请假')],
                default='present',
                max_length=20,
                verbose_name='签到状态'
            ),
        ),
        migrations.AddField(
            model_name='checkinrecord',
            name='status_note',
            field=models.CharField(blank=True, max_length=200, verbose_name='状态备注'),
        ),
    ]
