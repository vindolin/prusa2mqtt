# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='prusa2mqtt',
    version='0.2',
    author='Thomas Schüßler',
    description='Command line tool that parses the USB serial output of a Prusa printer and publishes the sensor values and progress to an MQTT server.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    keywords=['3d printing', 'serial', 'prusa', 'mqtt'],
    url='https://github.com/vindolin/prusa2mqtt',
    license='MIT',
    packages=['prusa2mqtt'],
    install_requires=[
        'paho-mqtt==1.6.1',
        'pyserial==3.5',
    ],
    entry_points={
        'console_scripts': ['prusa2mqtt=prusa2mqtt.main:main'],
    },
)
