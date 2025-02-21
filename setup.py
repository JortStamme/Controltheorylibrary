from setuptools import find_packages, setup

setup(
    name='controltheorylib',
    packages=find_packages(include=['controltheorylib']),
    version='0.1.0',
    description='Library for animating control theory',
    author='Jort Stammen',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)