from setuptools import setup, find_packages

setup(
    name="AIHub",
    version="0.1.0",
    packages=find_packages(include=['AIHub', 'AIHub.*']),
    install_requires=[
        'loguru',
        'pyyaml'
        'aiohttp',
        'openai',
        'setuptools',
        'dynaconf'
    ],
    author="ing-694",
    author_email="cpuburnt@gmail.com",
    description="An AI hub package",
    license="MIT",
    keywords="ai hub",
    url="https://github.com/ing-694/AIHub",
)
