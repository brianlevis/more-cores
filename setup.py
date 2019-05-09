import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="more-cores-brianlevis",
    version="0.0.1",
    author="Brian Levis",
    author_email="brianlevis1@gmail.com",
    description="High performance computing for those with no high performance computers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brianlevis/more-cores",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)