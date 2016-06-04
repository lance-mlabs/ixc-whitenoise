from __future__ import absolute_import

from pipeline.storage import PipelineMixin

from ixc_whitenoise.storage import CompressedManifestStaticFilesStorage


class PipelineCompressedManifestStaticFilesStorage(
        PipelineMixin, CompressedManifestStaticFilesStorage):
    pass
