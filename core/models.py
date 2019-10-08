from django.db import models
from django import forms
import datetime
TIME_CHOICES = [
    ('5', '5 λεπτά'),
    ('10', '10 λεπτά'),
    ('15', '15 λεπτά'),
    ('20', '20 λεπτά'),
    ('30', '30 λεπτά'),
    ('40', '40 λεπτά'),
    ('45', '45 λεπτά'),
    ('50', '50 λεπτά'),
    ('55', '55 λεπτά'),
    ('60', '1 ώρα'),
    ('75', '1:15 ώρες'),
    ('90', '1:30 ώρες'),
    ('105', '1:45 ώρες'),
    ('120', '2:00 ώρες'),
    ('150', '2:30 ώρες'),
    ('165', '2:45 ώρες'),
    ('180', '3:00 ώρες'),
    ('195', '3:15 ώρες'),
    ('210', '3:30 ώρες'),
    ('225', '3:45 ώρες'),
    ('240', '4:00 ώρες'),
    ('270', '4:30 ώρες'),
    ('300', '5:00 ώρες'),
    ('330', '5:30 ώρες'),
    ('360', '6:00 ώρες'),
    ('390', '6:30 ώρες'),
    ('420', '7:00 ώρες'),
    ('450', '7:30 ώρες'),
    ('480', '8:00 ώρες'),
]


class Clientele(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    task = models.CharField(max_length=255)

    def __str__(self):
        return self.task


class SubTask(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    mother_task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subtask = models.CharField(max_length=200)

    def __str__(self):
        return self.subtask


class ClientModel(models.Model):
    Aa = models.AutoField(primary_key=True, unique=True)
    name = models.ForeignKey(Clientele, on_delete=models.CASCADE)
    time_spent = models.CharField(max_length=20, choices=TIME_CHOICES)
    dec_name = models.CharField(max_length=100, default=None)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.date_added).split('.')[0] + ', ' \
               + self.name.name + ', ' + self.dec_name
