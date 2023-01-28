from setuptools import setup, find_packages

setup(
    name='flaskr',
    version='1.0.0',
    # Includes all python packages
    packages=find_packages(),
    # Includes all non-python files. Requires MANIFEST.in to tell what files to include
    include_package_data=True,
    install_requires=[
        'flask',
    ])
