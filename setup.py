import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftp_himawari8_hsd",
    version="1.0.6",
    author="Sasikala Gnanamuthu",
    author_email="serskg@nus.edu.sg",
    description="Sateliite Imagery Download Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gSasikala/Python_JAXA_Himawari8_Imagery_Downloader.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'argparse==1.4.0',
        'dateparser==1.0.0',
        'DateTime==4.3',
        'wget==3.2',
        'bz2file==0.98',
        'python-dateutil==2.8.1',
        'pathlib==1.0.1',
        'regex==2020.11.13',
        'futures3==1.0.0',
        'pandas~=1.2.4'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
