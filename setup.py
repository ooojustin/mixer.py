# python setup.py sdist bdist_wheel
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# pip install --index-url https://test.pypi.org/simple/ --no-deps mixer.py

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mixer.py",
    version="0.0.3",
    author="Justin Garofolo",
    author_email="justin@garofolo.net",
    description="An unofficial Mixer API wrapper written in Python. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ooojustin/mixer.py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
