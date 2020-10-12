import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="makedata-soi",
    version="0.0.1",
    author="soikode",
    description="A package to generate random data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soikode/MakeData",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)