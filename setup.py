import setuptools

# include additional packages as well - requests , tabulate , json

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysqlitecipher", # Replace with your own username
    version="0.22",
    author="Harsh Native",
    author_email="Harshnative@gmail.com",
    description="Ligth weigth and easy to use sqlite wrapper with built in encryption system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/harshnative/pysqlitecipher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
   'cryptography',
   'onetimepad',
    ],

    python_requires='>=3.6',
)