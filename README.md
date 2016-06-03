# What is this?

Improvements to [WhiteNoise][0]:

  * Serve media as well as static files.
  * Save media with hashed filenames, so they can be cached forever by a CDN.
  * Do not crash the ``collectstatic`` management command when a referenced
    file is not found or has an unknown scheme.

For Django 1.6, add `ixc_whitenoise_django16` to the top of `INSTALLED_APPS`.

[0]: https://github.com/evansd/whitenoise/
