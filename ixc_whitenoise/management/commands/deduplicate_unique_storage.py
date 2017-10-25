import logging

from django.core.management.base import BaseCommand
from django.db import models
from django.db.models.fields.files import FileField

from ixc_whitenoise.storage import UniqueStorage, unlazy_storage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deduplicate all file fields using `UniqueStorage`.'

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0

        # Loop through ALL models.
        for model in models.get_models():
            model_count = 0

            # Get all file fields that use `UniqueStorage`.
            file_fields = []
            for field in model._meta.fields:
                if isinstance(field, FileField):
                    storage = unlazy_storage(field.storage)
                    if isinstance(storage, UniqueStorage):
                        file_fields.append(field.name)

            # Skip models with no file fields.
            if not file_fields:
                continue

            # Loop through ALL instances.
            for instance in model.objects.all():
                updated = False

                # Loop through file fields.
                for field_name in file_fields:

                    field = getattr(instance, field_name)
                    original_name = field.name

                    # Skip empty fields.
                    if not field:
                        continue

                    # Skip fields that have already been deduplicated. First
                    # check that the filename looks like a valid hash (to save
                    # time when it is definitely not going to match), then check
                    # that the actual content hash matches the filename hash.
                    filename_hash = posixpath.split(
                        posixpath.splitext(original_name)[0])[1]
                    if re.match(r'^[0-f]{32}$', filename_hash):
                        content_hash = field.storage.get_content_hash(
                            original_name)
                        if content_hash == filename_hash:
                            logger.debug(
                                'Already deduplicated: %s.%s (pk: %s) %s' % (
                                    model._meta.model_name,
                                    field_name,
                                    instance.pk,
                                    original_name,
                                ))
                            continue

                    # Deduplicate.
                    try:
                        unique_name = field.storage.save(
                            original_name, field.file)
                    except:
                        logger.exception('Unable to save: %s.%s (pk: %s) %s' % (
                            model._meta.model_name,
                            field_name,
                            instance.pk,
                            original_name,
                        ))
                        continue

                    # Avoid keeping too many files open.
                    field.close()

                    # Something was updated.
                    if unique_name != original_name:
                        setattr(instance, field_name, unique_name)
                        logger.debug(
                            '%s, %s: %s.%s (pk: %s): %s -> %s' % (
                                updated_count + 1,
                                model_count + 1,
                                model._meta.model_name,
                                field_name,
                                instance.pk,
                                original_name,
                                unique_name,
                            ))
                        updated = True

                # Save and increment counters.
                if updated:
                    instance.save()
                    updated_count += 1
                    model_count += 1
                else:
                    skipped_count += 1

        # Done.
        logger.info('Updated: %s, Skipped: %s' % (
            updated_count,
            skipped_count,
        ))

