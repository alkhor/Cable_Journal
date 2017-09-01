from django.db import models

# Create your models here.
class Discover_data(models.Model):
    num = models.TextField()
    ip = models.TextField()
    mac = models.TextField()
    switch = models.TextField(default='-')
    port = models.TextField(default='-')
    def publish(self):
        self.save()
    def __str__(self):
        return self.num, self.ip, self.mac, self.port
