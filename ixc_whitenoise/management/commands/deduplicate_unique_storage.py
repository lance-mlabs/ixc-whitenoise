import logging
import os
import posixpath
import signal

from django.core.management.base import BaseCommand
from django.db import models
from django.db.models.fields.files import FileField

from ixc_whitenoise.models import UniqueFile
from ixc_whitenoise.storage import UniqueStorage, unlazy_storage

logger = logging.getLogger(__name__)

TERMINATE = False


class Command(BaseCommand):
    help = 'Deduplicate all file fields using `UniqueStorage`.'

    def handle(self, *args, **options):
        error_count = 0
        updated_count = 0
        skipped_count = 0

        # Loop through ALL models.
        for model in models.get_models():

            if TERMINATE:
                logger.error('Breaking out of outer loop.')
                break

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

            # Loop through ALL instances. Sort by primary key so we have some
            # kind of progress indicator as it counts down.
            for instance in model.objects.order_by('-pk'):

                if TERMINATE:
                    logger.error('Breaking out of inner loop.')
                    break

                updated = False

                # Loop through file fields.
                for field_name in file_fields:

                    field = getattr(instance, field_name)
                    original_name = field.name
                    unique_name = None

                    # Skip empty fields.
                    if not field:
                        continue

                    # Assume that files with a matching `UniqueFile` object (by
                    # unique name) have already been deduplicated, with nothing
                    # left to do.
                    unique_file = UniqueFile.objects \
                            .filter(name=original_name).last()
                    if unique_file:
                        skipped_count += 1
                        logger.debug(
                            '%s (%s), %s, %s: '
                            'Already deduplicated: '
                            '%s.%s (pk: %s) %s -> %s' % (
                                updated_count,
                                model_count,
                                skipped_count,
                                error_count,
                                model._meta.model_name,
                                field_name,
                                instance.pk,
                                unique_file.original_name,
                                unique_file.name,
                            ))
                        continue

                    # Assume that files with a matching `UniqueFile` object (by
                    # original name) have already been deduplicated, but we
                    # still need to update the field which is now pointing to a
                    # file that no longer exists.
                    unique_file = UniqueFile.objects \
                            .filter(original_name=original_name).last()
                    if unique_file:
                        unique_name = unique_file.name

                    # Skip fields with files that do not exist.
                    elif not field.storage.exists(field.name):
                        error_count += 1
                        logger.warning(
                            '%s (%s), %s, %s: '
                            'File does not exist: %s.%s (pk: %s) %s' % (
                                updated_count,
                                model_count,
                                skipped_count,
                                error_count,
                                model._meta.model_name,
                                field_name,
                                instance.pk,
                                original_name,
                            ))
                        continue

                    # Deduplicate.
                    else:
                        try:
                            unique_name = field.storage.save(
                                original_name, field.file)
                        except:
                            # Otherwise, log the exception and continue.
                            error_count += 1
                            logger.exception(
                                '%s (%s), %s, %s: '
                                'Unable to save: %s.%s (pk: %s) %s' % (
                                    updated_count,
                                    model_count,
                                    skipped_count,
                                    error_count,
                                    model._meta.model_name,
                                    field_name,
                                    instance.pk,
                                    original_name,
                                ))
                            continue
                        finally:
                            # Avoid keeping too many files open.
                            field.close()

                    # Something was updated.
                    if unique_name != original_name:
                        setattr(instance, field_name, unique_name)
                        updated = True
                        updated_count += 1
                        model_count += 1
                        logger.info(
                            '%s (%s), %s, %s: '
                            'Deduplicated: %s.%s (pk: %s) %s -> %s' % (
                                updated_count,
                                model_count,
                                skipped_count,
                                error_count,
                                model._meta.model_name,
                                field_name,
                                instance.pk,
                                original_name,
                                unique_name,
                            ))

                        # Cleanup original file and source directory.
                        field.storage.delete(original_name)
                        try:
                            os.removedirs(field.storage.path(
                                posixpath.dirname(original_name)))
                        except (NotImplementedError, OSError):
                            pass

                    # Nothing updated. This can happen when no matching
                    # `UniqueFile` exists for an already uniquely named file.
                    else:
                        skipped_count += 1
                        logger.debug(
                            '%s (%s), %s, %s: '
                            'Already uniquely named: %s.%s (pk: %s) %s' % (
                                updated_count,
                                model_count,
                                skipped_count,
                                error_count,
                                model._meta.model_name,
                                field_name,
                                instance.pk,
                                original_name,
                            ))

                # Save instance after all fields have been deduplicated.
                if updated:
                    instance.save()

        # Done.
        logger.info('Updated: %s, Skipped: %s, Errors: %s' % (
            updated_count,
            skipped_count,
            error_count,
        ))


# Allow graceful termination of current loop iteration.
# See: https://stackoverflow.com/questions/24426451/how-to-terminate-loop-gracefully-when-ctrlc-was-pressed-in-python
def signal_handler(signum, frame):
    global TERMINATE
    TERMINATE = True
    logger.error(
        'Keyboard Interrupt: Terminating after current loop iteration.')


signal.signal(signal.SIGINT, signal_handler)
