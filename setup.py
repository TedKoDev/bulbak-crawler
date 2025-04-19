from setuptools import setup, find_packages

setup(
    name="bulbak-crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        'console_scripts': [
            'bulbak-crawler=scheduler.runner:run_scheduler',
        ],
    },
) 