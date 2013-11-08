import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='django-db-faker',
    version='0.1',
    author='Florent Lebreton',
    author_email='florent.lebreton@makina-corpus.com',
    url='https://github.com/makinacorpus/django-db-faker',
    download_url="https://github.com/fle/django-db-faker/archive/master.zip",
    description="A module to help you faking a full django application database",
    long_description=open(os.path.join(here, 'README.rst')).read(),
    license='LPGL, see LICENSE file.',
    install_requires=['Django'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=['Topic :: Utilities',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Intended Audience :: Developers',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Development Status :: 4 - Beta',
                'Programming Language :: Python :: 2.7'],
)
