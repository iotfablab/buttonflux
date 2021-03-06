from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='buttonflux',
    version=1.2,
    description='Log Button Presses in InfluxDB and publish them to an MQTT broker',
    long_description=readme(),
    url='https://github.com/shantanoo-desai/buttonflux',
    author='Shantanoo Desai',
    author_email='shantanoo.desai@gmail.com',
    license='MIT',
    packages=['buttonflux'],
    scripts=['bin/buttonflux'],
    install_requires=[
        'evdev',
        'influxdb',
        'paho-mqtt'
    ],
    include_data_package=True,
    zip_safe=False)
