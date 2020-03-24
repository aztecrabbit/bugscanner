import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="bugscanner",
	version="0.0.1",
	author="aztecrabbit",
	author_email="aztecrabbit@yandex.com",
	description="bug scanner for internet freedom (domain fronting, server name indication, etc)",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/aztecrabbit/bugscan",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
	entry_points={
		'console_scripts': [
			'bugscanner=bugscanner.bugscanner:main',
		],
	},
)

