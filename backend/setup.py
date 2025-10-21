from setuptools import setup, find_packages

setup(
    name="system_rebellion",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'redis>=4.0.0',
        'prometheus-client>=0.9.0',
    ],
)
