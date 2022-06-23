from setuptools import setup, find_packages

setup(
    name='captiveportal',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        'flask==1.1.1',
        'requests==2.22.0',
        'ua_parser==0.8.0',
        'gunicorn==20.0.4',
        'itsdangerous==1.1',   # 3.5 support dropped 15Apr2020, so must use 1.1
        'MarkupSafe==1.1.1',  # 3.5 support dropped 30Jan2020
        'Jinja2==2.11.3',  # 3.5 support dropped 27Jan2020
    ],
)
