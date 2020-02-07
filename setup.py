import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pandaforce",
    version="1.1.0",
    author="Jamil Vallis-Walker",
    author_email="",
    description="A pandas and simple-salesforce based utility package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jwok90/pandaforce",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
