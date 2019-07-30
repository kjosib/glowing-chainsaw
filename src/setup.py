import setuptools

setuptools.setup(
	name='cubicle',
	include_package_data=True,
	version='0.0.1',
	packages=['cubicle', ],
	license='MIT',
	description='A declarative DSL for high-functioning business-oriented tabular and hierarchical reporting',
	long_description=open('README.md').read(),
	long_description_content_type="text/markdown",
	url="https://github.com/kjosib/project-cubicle",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Developers",
		"Topic :: Office/Business",
		"Topic :: Software Development :: Interpreters",
		"Topic :: Software Development :: Libraries",
		"Programming Language :: Python :: 3 :: Only",
    ],
)