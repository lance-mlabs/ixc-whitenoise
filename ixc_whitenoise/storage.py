import hashlib
import logging
import posixpath
import re

from django.core.files.storage import FileSystemStorage
from whitenoise.storage import \
    CompressedManifestStaticFilesStorage, HelpfulExceptionMixin, \
    MissingFileError

logger = logging.getLogger(__name__)


# Log a warning instead of raising an exception when a referenced file is
# not found. These are often in 3rd party packages and outside our control.
class HelpfulWarningMixin(HelpfulExceptionMixin):

    def make_helpful_exception(self, exception, name):
        exception = super(HelpfulWarningMixin, self) \
            .make_helpful_exception(exception, name)
        if isinstance(exception, MissingFileError):
            logger.warning('\n\nWARNING: %s' % exception)
            return False
        return exception


# Don't try to rewrite URLs with unknown schemes.
class RegexURLConverterMixin(object):

    def url_converter(self, name, template=None):
        converter = super(RegexURLConverterMixin, self) \
            .url_converter(name, template)

        def custom_converter(matchobj):
            matched, url = matchobj.groups()
            if re.match(r'(?i)([a-z]+://|//|#|data:)', url):
                return matched
            return converter(matchobj)

        return custom_converter


class CompressedManifestStaticFilesStorage(
        HelpfulWarningMixin,
        RegexURLConverterMixin,
        CompressedManifestStaticFilesStorage):
    pass


# Save media with hashed filenames, so they can be cached forever by a CDN.
class HashedMediaStorage(FileSystemStorage):

    # Disable Django's name conflict resolution.
    def get_available_name(self, name):
        return name

    def _save(self, name, content):
        # Get hash from content.
        md5 = hashlib.md5()
        for chunk in content.chunks():
            md5.update(chunk)
        file_hash = md5.hexdigest()[:12]

        # Add hash to name.
        name, ext = posixpath.splitext(name)
        name = '%s.%s%s' % (name, file_hash, ext)

        # Return early without saving, because existing files must have the
        # same content.
        if self.exists(name):
            return name

        return super(HashedMediaStorage, self)._save(name, content)
