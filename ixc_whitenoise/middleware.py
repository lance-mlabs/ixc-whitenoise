from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.http import FileResponse
from django.utils.functional import empty
from django.utils.six.moves.urllib.parse import urlparse
from whitenoise.middleware import WhiteNoiseMiddleware
from whitenoise.utils import ensure_leading_trailing_slash

from ixc_whitenoise.storage import UniqueStorage


class StripVaryHeaderMiddleware(object):

    def process_response(self, request, response):
        """
        Remove `Vary` header to work around an IE bug. See:
        http://stackoverflow.com/a/23410136
        """
        if isinstance(response, FileResponse):
            del response['vary']
        return response


# Serve media as well as static files.
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
        # Ensure the lazy default storage object has been evaluated, so we can
        # test the wrapped storage class.
        if default_storage._wrapped is empty:
            default_storage._setup()
        if isinstance(default_storage._wrapped, UniqueStorage) and \
                url.startswith(self.media_prefix):
            return True
        return False
