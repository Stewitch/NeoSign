from django.conf import settings
from django.db import models


class Activity(models.Model):
	name = models.CharField(max_length=200, verbose_name='活动名称')
	description = models.TextField(blank=True, verbose_name='活动描述')
	start_time = models.DateTimeField(verbose_name='开始时间')
	end_time = models.DateTimeField(verbose_name='结束时间')
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='created_activities',
		verbose_name='创建人',
	)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
	is_active = models.BooleanField(default=True, verbose_name='是否启用')

	participants = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		through='ActivityParticipation',
		related_name='activities',
		verbose_name='参与用户',
	)

	class Meta:
		verbose_name = '活动'
		verbose_name_plural = '活动'
		ordering = ['-start_time']

	def __str__(self) -> str:  # pragma: no cover - simple display
		return self.name


class ActivityParticipation(models.Model):
	activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
	can_participate = models.BooleanField(default=True, verbose_name='允许参与')

	class Meta:
		unique_together = ('activity', 'user')
		verbose_name = '参与关系'
		verbose_name_plural = '参与关系'

	def __str__(self) -> str:  # pragma: no cover - simple display
		return f"{self.user} -> {self.activity}"


class CheckInRecord(models.Model):
	activity = models.ForeignKey(
		Activity, on_delete=models.CASCADE, related_name='checkins', verbose_name='活动'
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins', verbose_name='用户'
	)
	checkin_time = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')
	ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
	user_agent = models.TextField(blank=True, verbose_name='UserAgent')

	class Meta:
		unique_together = ('activity', 'user')
		ordering = ['-checkin_time']
		verbose_name = '签到记录'
		verbose_name_plural = '签到记录'

	def __str__(self) -> str:  # pragma: no cover - simple display
		return f"{self.user} - {self.activity}"
