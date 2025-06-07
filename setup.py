from setuptools import find_packages, setup, find_packages


with open("README.md", "r") as f:
    description = f.read()

setup(
    name='controltheorylib',
    packages=find_packages(include=['controltheorylib']),
    version='0.1.2',
    description='Library for animating key control theory concepts',
    author='Jort Stammen',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',long_description=description,
    license='MIT',
    long_description_content_type="text/markdown",
    url='https://github.com/JortStamme/Controltheorylibrary'
)