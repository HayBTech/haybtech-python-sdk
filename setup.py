from setuptools import setup, find_packages

setup(
    name="haybtech-sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],  # Zero dependencies for maximum security
    author="HayBTech Team",
    description="Official Python SDK for HayBTech Payment Gateway",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/haybtech/python-sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
