from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkin', '0003_checkinrecord_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkinrecord',
            name='status',
            field=models.CharField(
                choices=[
                    ('present', '已签到'),
                    ('proxy', '代签'),
                    ('excused', '请假'),
                    ('absent', '未签')
                ],
                default='present',
                max_length=20,
                verbose_name='签到状态'
            ),
        ),
    ]
