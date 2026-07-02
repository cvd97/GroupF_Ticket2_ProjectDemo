from django.db import models

class NotificationLog(models.Model):
    event_type = models.CharField(max_length=80)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    selected_channels = models.CharField(max_length=200)
    final_status = models.CharField(max_length=40)
    pattern_trace = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
