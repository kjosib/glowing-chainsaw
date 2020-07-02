"""
Packaging script for PyPI.
"""

import setuptools

setuptools.setup(
	name='cubicle',
	author='Ian Kjos',
	author_email='kjosib@gmail.com',
	version='0.8.7', # Might break a few things, probably won't.
	packages=['cubicle', ],
	package_dir = {'': 'src'},
	package_data={
		'cubicle': ['core.md',],
	},
	license='MIT',
	description='a high-level declarative domain-specific language for high-functioning, professional-looking, business-oriented numerical and graphical reporting',
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
	install_requires=[
		'xlsxwriter', 'booze-tools>=0.4.3'
	]
)