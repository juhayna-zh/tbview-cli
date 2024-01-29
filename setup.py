from setuptools import setup

setup(
    name='tbview-cli',
    author='juhayna',
    maintainer='juhayna_zh',
    version='0.1',
    description="A command line interface for Tensorboard visualization",
    packages = ['tbview'],
    exclude_package_data = {'': ['assets/*']},
    install_requires= [
        'plotext',
        'blessed',
        'inquirer',
        'protobuf==3.20.1',
    ],
    entry_points={
        'console_scripts': [
            'tbview = tbview.cli:main'
        ]
    },
)