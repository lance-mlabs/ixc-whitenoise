import setuptools

setuptools.setup(
    name='ixc-whitenoise',
    use_scm_version={'version_scheme': 'post-release'},
    packages=setuptools.find_packages(),
    install_requires=[
        'whitenoise>=3.1',
    ],
    extras_require={
        'pipeline': [
            'django-pipeline',
        ],
    },
    setup_requires=['setuptools_scm'],
)
