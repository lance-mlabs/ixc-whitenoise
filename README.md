# What is this?

Improvements to [WhiteNoise][0]:

  * Serve media as well as static files.
  * Save media with hashed filenames, so they can be cached forever by a CDN.
  * Do not crash the ``collectstatic`` management command when a referenced
    file is not found or has an unknown scheme.
  * Add [django-pipeline][1] integration.
  * Add support for Django 1.6 via monkey patching.
  * Strip the `Vary` header for static file responses via middleware, to work
  	around an IE bug. This should come *before* `SessionMiddleware` in
  	`MIDDLEWARE_CLASSES`. See: http://stackoverflow.com/a/23410136

[0]: https://github.com/evansd/whitenoise/
[1]: https://github.com/jazzband/django-pipeline/
