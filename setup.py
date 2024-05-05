from setuptools import setup, find_packages

setup(
    name='pyOpenTTDAdmin',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],  # Add any dependencies here
    author='liki-mc',
    description='Python library to communicate with OpenTTD Admin port',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/liki-mc/pyOpenTTDAdmin/',
    license='MIT',  # Choose an appropriate license
)
