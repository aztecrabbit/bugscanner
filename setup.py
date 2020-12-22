import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="bugscanner",
	version="0.1.8",
	author="aztecrabbit",
	author_email="ars.xda@gmail.com",
	description="Bug Scanner for Internet Freedom (Domain Fronting, Server Name Indication, Etc)",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/aztecrabbit/bugscanner",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
	entry_points={
		'console_scripts': [
			'bugscanner=bugscanner.__main__:main',
		],
	},
)
