# Generated by Django 3.2.7 on 2021-11-17 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ixc_whitenoise', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uniquefile',
            name='name',
            field=models.CharField(db_index=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='uniquefile',
            name='original_name',
            field=models.CharField(db_index=True, max_length=500),
        ),
    ]