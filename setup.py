from setuptools import setup, find_packages

setup(
	name='project3',
	version='1.0',
	author='Sakshi Pandey',
	author_email='sakshi.pandey@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs', 'resources')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)
