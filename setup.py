#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py based on https://github.com/navdeep-G/setup.py

import io
import os
import sys
from setuptools import find_packages, setup, Command

# Package meta-data
REQUIRES_PYTHON = ">=3.6.0"

REQUIRES = ["jinja2", "pyyaml", "digraphtools"]
EXTRAS = {}
SETUP_REQUIRES = ["setuptools_scm"]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Load the package's __package_metadata__.py module as a dictionary.
about = {}
NAME = "codesmith"
with open(os.path.join(here, NAME, "__package_metadata__.py")) as f:
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


setup(
    name=about["__package_name__"],
    use_scm_version=True,
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    python_requires=REQUIRES_PYTHON,
    url=about["__url__"],
    py_modules=["codesmith"],
    entry_points={"console_scripts": ["csmake=codesmith.cli:main"]},
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    setup_requires=SETUP_REQUIRES,
    include_package_data=True,
    license=about["__license__"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Build Tools",
    ],
    cmdclass={"upload": UploadCommand},
)
