from django.db import models

TIME_CHOICES = [
    ('5', '5 λεπτά'),
    ('10', '10 λεπτά'),
    ('15', '15 λεπτά'),
    ('20', '20 λεπτά'),
    ('30', '30 λεπτά'),
    ('45', '45 λεπτά'),
    ('60', '1 ώρα'),
    ('90', '1:30 ώρες'),
    ('120', '2:00 ώρες'),
    ('150', '2:30 ώρες'),
    ('180', '3:00 ώρες'),
    ('210', '3:30 ώρες'),
    ('240', '4:00 ώρες'),
]

class Clientele(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Task(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ClientModel(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    name = models.ForeignKey(Clientele, on_delete=models.CASCADE)
    time_spent = models.CharField(max_length=20, choices=TIME_CHOICES)
    dec_name = models.CharField(max_length=100, default=None)
    reason = models.ForeignKey(Task, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.date_added).split(' ')[0] + ', ' \
               + self.name.name + ', ' + self.dec_name
