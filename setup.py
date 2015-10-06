from setuptools import setup


def read(filename):
    with open(filename) as f:
        return f.read()


setup(
    name="urlclustering",
    version="0.3",
    author="Dimitris Giannitsaros",
    author_email="daremon@gmail.com",
    description="Facilitate clustering of similar URLs of a website",
    long_description=read("README.rst"),
    license="MIT",
    keywords="cluster clustering urls",
    url="https://github.com/daremon/urlclustering",
    packages=['urlclustering'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
