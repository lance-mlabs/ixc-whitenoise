# What is this?

Improvements to [WhiteNoise][0]:

  * Serve media as well as static files.
  * Save media with hashed filenames, so they can be cached forever by a CDN.
  * Do not crash the ``collectstatic`` management command when a referenced
    file is not found or has an unknown scheme.
  * Add support for Django 1.6 via monkey patching.

[0]: https://github.com/evansd/whitenoise/
