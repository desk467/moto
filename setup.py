import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("status_page/requirements.txt") as fr:
    install_reqs = fr.read().splitlines()

setuptools.setup(
    name='status_page',
    version='0.1',
    scripts=['status_page/bin/status_page_cli'],
    author="Ricardo Gomes",
    author_email="desk467@gmail.com",
    description="A Status Page for your infrastructure",
    install_requires=install_reqs,
    long_description=long_description,
    include_package_data=True,
    long_description_content_type="text/markdown",
    url="https://github.com/desk467/status_page",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
