from setuptools import setup

setup(
    name = 'pyOpenTTDAdmin',
    version = '1.0.1',
    packages = ['pyopenttdadmin', 'aiopyopenttdadmin'],
    install_requires = [],  # Add any dependencies here
    author = 'liki-mc',
    description = 'Python library to communicate with OpenTTD Admin port',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/liki-mc/pyOpenTTDAdmin/',
    license = 'MIT',  # Choose an appropriate license
)