# Generated by Django 2.2.4 on 2019-09-02 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='subtask',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
