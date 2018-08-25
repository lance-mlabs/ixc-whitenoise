# What is this?

Improvements to [WhiteNoise][0]:

  * Serve media as well as static files.
  * Save media with unique filenames, so they can be deduplicated and cached
    forever.
  * Store the original name for deduplicated files in the `UniqueFile` model.
  * Do not crash the ``collectstatic`` management command when a referenced
    file is not found or has an unknown scheme.
  * Add [django-pipeline][1] integration.
  * Add support for Django 1.6 via monkey patching.
  * Strip the `Vary` header for static file responses via middleware, to work
  	around an IE bug. This should come *before* `SessionMiddleware` in
  	`MIDDLEWARE_CLASSES`. See: http://stackoverflow.com/a/23410136

Settings:

  * `IXC_WHITENOISE_DEDUPE_EXTENSIONS` - A dictionary mapping extension
    variations to canonical versions. Unique files will use the canonical
    version. Default: `{'.jpeg': '.jpg', '.yaml': '.yml'}`.

  * `IXC_WHITENOISE_DEDUPE_PATH_PREFIX` - Unique files will be saved into this
    directory. Their original path will be retained, but their filename will be
    replaced with a unique content hash. Default: `dd`.

  * `IXC_WHITENOISE_ORIGINAL_BASENAME` - Append an abbreviated content hash to
    the original basename instead of replacing it with a full content hash.
    This reduces deduplicate, but may be better for SEO. Default: `False`.

  * `IXC_WHITENOISE_ORIGINAL_BASENAME_HASH_LENGTH` - The number of characters
    from the full content hash to use as an abbreviated hash. Default: `7`.

Management commands:

  * `deduplicate_unique_storage` - Finds all file fields in all models that use
    `UniqueStorage` and re-saves them to deduplicate. The original files are not
    removed. Files that have already been deduplicated will be skipped.

[0]: https://github.com/evansd/whitenoise/
[1]: https://github.com/jazzband/django-pipeline/
