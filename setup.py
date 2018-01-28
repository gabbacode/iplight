from setuptools import setup

setup(name='iplight',
      version='0.0.0.1',
      description='iplight is a client for network controled lights',
      long_description='iplight is a client for network controled lights using tlv protocol',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: tcpip :: tlv :: iot',
      ],
      keywords='iplight iot tlv',
      url='https://github.com/gabbacode/iplight',
      author='gabba',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['iplight'],
      install_requires=[
          'asyncio'
      ],
      include_package_data=True,
      zip_safe=False)

