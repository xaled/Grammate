#!/usr/bin/env python3
from setuptools import setup

VERSION = '1.0.0'  # major.minor.fix
URL = 'https://github.com/xaled/Grammate'
DESCRIPTION = 'A Python tool that merges multi-file modules into a single, self-contained script.'


def convert_rst(markdown_text, fallback_rst=None):
    try:
        import pypandoc
        return pypandoc.convert_text(markdown_text, 'rst', format='md')
    except:
        try:
            import m2r2
            return m2r2.convert(markdown_text)
        except:
            return fallback_rst or markdown_text


def load_requirements(requirements_file="requirements.txt"):
    try:
        with open(requirements_file, 'r') as fin:
            requirements = [line.split('#')[0].strip() for line in fin]
            requirements = [line for line in requirements if line]
        return requirements
    except FileNotFoundError:
        print(f"Requirements file '{requirements_file}' not found.")
        return []
    except Exception as e:
        print(f"Error loading requirements: {e}")
        return []


with open('README.md', 'r') as f:
    long_description = convert_rst(f.read().replace('\n\n', '\n'))

with open('LICENSE', 'r') as f:
    license_text = f.read()

if __name__ == "__main__":
    setup(
        name='grammate',
        version=VERSION,
        description=DESCRIPTION,
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
        url=URL,
        install_requires=load_requirements(),
        python_requires='>=3',
        packages=['grammate'],
        package_data={
            '': ['LICENSE', 'requirements.txt', 'README.md'],
        },
    )
