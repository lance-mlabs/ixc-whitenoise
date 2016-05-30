import setuptools

setuptools.setup(
    name='ixc-whitenoise',
    use_scm_version={'version_scheme': 'post-release'},
    py_modules=['ixc_whitenoise'],
    install_requires=[
        'whitenoise>=3.1',
    ],
    setup_requires=['setuptools_scm'],
)
