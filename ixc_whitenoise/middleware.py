import posixpath

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.utils.functional import empty
from six.moves.urllib.parse import urlparse
from whitenoise.middleware import WhiteNoiseMiddleware

try:
    from whitenoise.string_utils import ensure_leading_trailing_slash  # >=4.0b1
except ImportError:
    from whitenoise.utils import ensure_leading_trailing_slash

from ixc_whitenoise.storage import UniqueMixin, unlazy_storage


class StripVaryHeaderMiddleware(object):

    def process_response(self, request, response):
        """
        Remove `Vary` header to work around an IE bug. See:
        http://stackoverflow.com/a/23410136
        """
        # FileResponse was added in Django 1.7.4. Do nothing when it is not
        # available.
        try:
            from django.http import FileResponse
        except ImportError:
            return response
        if isinstance(response, FileResponse):
            del response['vary']
        return response


# Serve media as well as static files.
# Redirect requests for deduplicated unique storage.
class WhiteNoiseMiddleware(WhiteNoiseMiddleware):

    config_attrs = WhiteNoiseMiddleware.config_attrs + ('media_prefix', )
    media_prefix = None

    def __init__(self, *args, **kwargs):
        super(WhiteNoiseMiddleware, self).__init__(*args, **kwargs)
        if self.media_root:
            self.add_files(self.media_root, prefix=self.media_prefix)

    def check_settings(self, settings):
        super(WhiteNoiseMiddleware, self).check_settings(settings)
        if self.media_prefix == '/':
            media_url = getattr(settings, 'MEDIA_URL', '').rstrip('/')
            raise ImproperlyConfigured(
                'MEDIA_URL setting must include a path component, for '
                'example: MEDIA_URL = {0!r}'.format(media_url + '/media/')
            )

    def configure_from_settings(self, settings):
        self.media_prefix = urlparse(settings.MEDIA_URL or '').path
        super(WhiteNoiseMiddleware, self).configure_from_settings(settings)
        self.media_prefix = ensure_leading_trailing_slash(self.media_prefix)
        self.media_root = settings.MEDIA_ROOT

    # Files with unique names are always immutable.
    def is_immutable_file(self, path, url):
        if super(WhiteNoiseMiddleware, self).is_immutable_file(path, url):
            return True
        # `MEDIA_ROOT` and `MEDIA_URL` are used with the default storage class.
        # Only assume media is immutable if `UniqueMixin` is the default
        # storage class.
        storage = unlazy_storage(default_storage)
        if isinstance(storage, UniqueMixin) and \
                url.startswith(self.media_prefix):
            return True
        return False

    def process_response(self, request, response, *args, **kwargs):
        """
        Redirect requests for deduplicated unique storage.
        """
        from ixc_whitenoise.models import UniqueFile  # Avoid circular import
        if response.status_code == 404 and \
                request.path_info.startswith(self.media_prefix):
            original_name = request.path_info[len(self.media_prefix):]
            # There could be more than one `UniqueFile` object for a given
            # name. Redirect to the most recently deduplicated one.
            unique_file = UniqueFile.objects \
                .filter(original_name=original_name).last()
            if unique_file:
                response = HttpResponseRedirect(posixpath.join(
                    self.media_prefix,
                    unique_file.name,
                ))
        return response
