# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UniqueFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('original_name', models.CharField(db_index=True, max_length=255)),
            ],
            options={
                'ordering': ('-pk',),
            },
        ),
    ]
