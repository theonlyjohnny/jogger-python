from setuptools import setup, find_packages

setup(
    name='python-logger',
    version='1.0.0',
    description='Python3 Logger',
    url='http://github.com/theonlyjohnny/python-logger',
    author='Johnny Dallas',
    author_email='theonlyjohnny@theonlyjohnny.sh',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'colorlog'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False
)
