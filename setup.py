"""
Packaging script for PyPI.
"""

import setuptools

setuptools.setup(
	name='cubicle',
	author='Ian Kjos',
	author_email='kjosib@gmail.com',
	include_package_data=True,
	version='0.0.1',
	packages=['cubicle', ],
	package_dir = {'': 'src'},
	license='MIT',
	description='A declarative DSL for high-functioning business-oriented tabular and hierarchical reporting',
	long_description=open('README.md').read(),
	long_description_content_type="text/markdown",
	url="https://github.com/kjosib/glowing-chainsaw",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"Topic :: Office/Business",
		"Topic :: Software Development :: Interpreters",
		"Topic :: Software Development :: Libraries",
		
    ],
	python_requires='>=3.7',
)