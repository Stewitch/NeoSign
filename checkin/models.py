from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from datetime import time as dt_time
import hashlib
import os


def generate_qr_secret() -> str:
	return hashlib.sha256(os.urandom(16)).hexdigest()[:32]


class Activity(models.Model):
	name = models.CharField(max_length=200, verbose_name='活动名称')
	description = models.TextField(blank=True, verbose_name='活动描述')
	start_time = models.DateTimeField(verbose_name='开始时间')
	end_time = models.DateTimeField(verbose_name='结束时间')
	# 位置签到
	location_enabled = models.BooleanField(default=False, verbose_name='启用位置限制')
	location_lat = models.FloatField(null=True, blank=True, verbose_name='纬度')
	location_lng = models.FloatField(null=True, blank=True, verbose_name='经度')
	location_radius_m = models.PositiveIntegerField(default=0, verbose_name='范围(米)')
	# 重复签到
	repeat_type = models.CharField(
		max_length=10,
		choices=(('none', '不重复'), ('daily', '每日'), ('weekly', '每周')),
		default='none',
		verbose_name='重复方式',
	)
	repeat_weekdays = models.JSONField(default=list, verbose_name='每周重复日(1-7)')
	window_start_time = models.TimeField(null=True, blank=True, verbose_name='每日开始时刻')
	window_end_time = models.TimeField(null=True, blank=True, verbose_name='每日结束时刻')
	# 二维码签到
	qr_enabled = models.BooleanField(default=False, verbose_name='启用二维码')
	qr_refresh_interval_s = models.PositiveIntegerField(
		default=30, validators=[MinValueValidator(10)], verbose_name='二维码刷新周期(秒)'
	)
	qr_secret = models.CharField(max_length=32, default=generate_qr_secret, verbose_name='二维码密钥')
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

	def is_open_for(self, dt):
		if not self.is_active:
			return False
		if self.repeat_type == 'none':
			return self.start_time <= dt <= self.end_time
		# 总体有效期：使用日期边界
		start_date = self.start_time.date()
		end_date = self.end_time.date() if self.end_time else None
		current_date = dt.date()
		if current_date < start_date:
			return False
		if end_date and current_date > end_date:
			return False
		# 时间窗：缺失则退化为全天
		start_window = self.window_start_time or dt_time(0, 0)
		end_window = self.window_end_time or dt_time(23, 59, 59)
		current_time = dt.time()
		if start_window <= end_window:
			if not (start_window <= current_time <= end_window):
				return False
		else:
			# 跨午夜窗口，例如 23:00-01:00
			if not (current_time >= start_window or current_time <= end_window):
				return False
		if self.repeat_type == 'weekly':
			weekday = dt.isoweekday()  # 1-7
			return weekday in (self.repeat_weekdays or [])
		# daily
		return True

	def current_qr_token(self, dt=None):
		dt = dt or timezone.now()
		interval = max(self.qr_refresh_interval_s or 30, 10)
		slot = int(dt.timestamp() // interval)
		payload = f"{self.qr_secret}:{slot}"
		return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]

	def is_valid_qr_token(self, token, dt=None):
		if not (self.qr_enabled and token):
			return False
		return token == self.current_qr_token(dt)

	@property
	def is_ongoing(self) -> bool:
		"""Convenience flag for UI to show current status.
		Uses `is_open_for(now)` for both single and repeating activities.
		"""
		return self.is_open_for(timezone.now())


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
	class CheckInStatus(models.TextChoices):
		PRESENT = ('present', _('已签到'))
		PROXY = ('proxy', _('代签'))
		EXCUSED = ('excused', _('请假'))
		ABSENT = ('absent', _('未签'))

	activity = models.ForeignKey(
		Activity, on_delete=models.CASCADE, related_name='checkins', verbose_name='活动'
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins', verbose_name='用户'
	)
	checkin_time = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')
	ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
	user_agent = models.TextField(blank=True, verbose_name='UserAgent')
	# 位置数据（若启用）
	latitude = models.FloatField(null=True, blank=True, verbose_name='签到纬度')
	longitude = models.FloatField(null=True, blank=True, verbose_name='签到经度')
	status = models.CharField(
		max_length=20,
		choices=CheckInStatus.choices,
		default=CheckInStatus.PRESENT,
		verbose_name='签到状态',
	)
	status_note = models.CharField(max_length=200, blank=True, verbose_name='状态备注')

	class Meta:
		unique_together = ('activity', 'user')
		ordering = ['-checkin_time']
		verbose_name = '签到记录'
		verbose_name_plural = '签到记录'

	def __str__(self) -> str:  # pragma: no cover - simple display
		return f"{self.user} - {self.activity}"
