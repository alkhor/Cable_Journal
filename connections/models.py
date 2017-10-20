from django.db import models

# Create your models here.
class DiscoverData(models.Model):
    num = models.TextField()
    ip = models.TextField()
    mac = models.TextField()
    switch = models.TextField(default='-')
    port = models.TextField(default='-')
    def publish(self):
        self.save()
    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(self.num, self.ip, self.mac, self.port, self.switch, self.id)
