import setuptools
from m2r import convert

with open("README.md", "r") as f:
    long_description = convert(f.read())

setuptools.setup(
    name="CherrypyScheduler",
    version="0.1",
    author="SawyerSteven",
    author_email="sawyerstevenk@gmail.com",
    description="Repeating task scheduler for Cherrypy webserver!",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sawyersteven/CherrypyScheduler",
    packages=setuptools.find_packages(),
    classifiers=(
		"Programming Language :: Python 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)