import sys

from django.core.management.base import BaseCommand
from django.db import models
from django.db.models.fields.files import FileField


class Command(BaseCommand):
    help = 'Re-save all file fields using `UniqueStorage` to deduplicate.'

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0

        # Loop through ALL models.
        for model in models.get_models():
            model_count = 0

            # Get all file fields that use `UniqueStorage`.
            file_fields = []
            for field in model._meta.fields:
                if isinstance(field, FileField) and \
                        isinstance(field.storage, UniqueStorage):
                    file_fields.append(field.name)

            # Skip models with no file fields.
            if not file_fields:
                continue

            # Loop through ALL instances.
            for instance in model.objects.all():
                updated = False

                # Loop through file fields.
                for field_name in file_fields:

                    # Re-save field to deduplicate.
                    field = getattr(instance, field_name)
                    name = field.name
                    field.save(field.name, field.file)

                    # Something was updated.
                    if name != field.name:
                        updated = True
                        sys.stderr.write(
                            '%s: %s: %s (pk: %s) %s: %s -> %s\n' % (
                                updated_count + 1,
                                model._meta.model_name,
                                model_count + 1,
                                instance.pk,
                                field_name,
                                name,
                                field.name,
                            ))

                # Increment counters.
                if updated:
                    updated_count += 1
                    model_count += 1
                else:
                    skipped_count += 1

        # Done.
        sys.stderr.write('updated: %s, skipped: %s' % (
            updated_count,
            skipped_count,
        ))

