from django.db import models


class UniqueFile(models.Model):
    name = models.CharField(db_index=True, max_length=255)
    original_name = models.CharField(db_index=True, max_length=255)

    class Meta:
        ordering = ('-pk', )
        unique_together = ('name', 'original_name', )
