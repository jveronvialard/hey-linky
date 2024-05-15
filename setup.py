from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name="linky",
    version="0.0.1",
    description="Linky, your personalized content companion",
    packages=find_packages(),
    install_requires=requirements,
)
