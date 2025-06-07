from setuptools import setup, find_packages

setup(
    name='audittrail',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scipy',
        'ipython',
    ],
)
