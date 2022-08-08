#! /usr/bin/env python

import setuptools

setuptools.setup(
    name="cdisc-rules-engine",
    version="0.1.0",
    description="Open source offering of the cdisc rules engine",
    author="cdisc-org",
    url="https://github.com/cdisc-org/cdisc-rules-engine",
    packages=setuptools.find_packages(),
    license="MIT",
    python_requires=">=3.9",
    install_requires=[
        "pytest==7.1.2",
        "pandas==1.3.5",
        "business-rules-enhanced==1.2.1",
        "python-dotenv==0.20.0",
        "cdisc-library-client==0.1.4",
        "pytest-asyncio==0.18.3",
        "azure-storage-blob==12.3.1",
        "azure-cosmos==4.3.0",
        "odmlib==0.1.4",
        "xport==3.6.1",
        "redis==4.0.2",
        "black==22.6.0",
        "pre-commit==2.20.0",
        "openpyxl==3.0.10",
        "click==8.1.3",
        "pyinstaller==5.2",
    ],
)
