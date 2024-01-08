# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

exec(open('mcs/version.py').read())

setuptools.setup(
    name="mcs",
    version=__version__,
    author="Martin Mengel",
    author_email="martinm@miltenyi._com",
    description="Miltenyi CAN system package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.miltenyibiotec.com",
    license="proprietary and confidential",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
