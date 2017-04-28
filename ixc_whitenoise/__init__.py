import ixc_whitenoise.monkeypatch_django16

from ixc_whitenoise.middleware import \
    StripVaryHeaderMiddleware, WhiteNoiseMiddleware
from ixc_whitenoise.storage import \
    CompressedManifestStaticFilesStorage, HashedMediaStorage
