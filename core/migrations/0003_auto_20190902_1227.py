# Generated by Django 2.2.4 on 2019-09-02 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_subtask_subtask'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientmodel',
            old_name='sub_reason',
            new_name='subtask',
        ),
        migrations.RenameField(
            model_name='clientmodel',
            old_name='reason',
            new_name='task',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='name',
            new_name='task',
        ),
        migrations.AlterField(
            model_name='clientmodel',
            name='time_spent',
            field=models.CharField(choices=[('5', '5 λεπτά'), ('10', '10 λεπτά'), ('15', '15 λεπτά'), ('20', '20 λεπτά'), ('30', '30 λεπτά'), ('45', '45 λεπτά'), ('60', '1 ώρα'), ('75', '1:15 ώρες'), ('90', '1:30 ώρες'), ('105', '1:45 ώρες'), ('120', '2:00 ώρες'), ('150', '2:30 ώρες'), ('165', '2:45 ώρες'), ('180', '3:00 ώρες'), ('195', '3:15 ώρες'), ('210', '3:30 ώρες'), ('225', '3:45 ώρες'), ('240', '4:00 ώρες')], max_length=20),
        ),
    ]
