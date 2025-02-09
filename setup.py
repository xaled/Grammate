#!/usr/bin/env python3
from distutils.core import setup

VERSION = '1.0.0'  # major.minor.fix

with open('README.md', 'r') as f:
    long_description = f.read()

with open('LICENSE', 'r') as f:
    license_text = f.read()

if __name__ == "__main__":
    setup(
        name='grammate',
        version=VERSION,
        description='Grammate is a lightweight Python module for localization based on formal grammars.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        keywords='grammar localization',
        author='Khalid Grandi',
        author_email='kh.grandi@gmail.com',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ],
        license='MIT',
        url='https://github.com/xaled/Grammate',
        install_requires=['PyYAML'],
        python_requires='>=3',
        packages=['grammate'],
        package_data={
            '': ['LICENSE', 'requirements.txt', 'README.md'],
        },
    )