from django.db import models


class UniqueFile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(db_index=True, max_length=255)
    original_name = models.CharField(db_index=True, max_length=255)

    class Meta:
        ordering = ('-pk', )
