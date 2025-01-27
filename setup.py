from setuptools import setup, find_packages

setup(
    name='gpt-worker',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'openai',
    ],
    entry_points={
        'console_scripts': [
            'gptw=gpt_worker.cli:cli',
        ],
    },
)
