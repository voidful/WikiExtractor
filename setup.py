from setuptools import setup, find_packages

setup(
    name='wikiext',
    version='0.0.7',
    description='Wiki Extractor ',
    url='https://github.com/voidful/WikiExtractor',
    author='Voidful',
    author_email='voidful.stack@gmail.com',
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        'Programming Language :: Python :: 3.5'
    ],
    license="Apache",
    keywords='wikiext wikiextactor extractor',
    packages=find_packages(),
    install_requires=[
        "gensim",
        "tqdm",
        "nlp2",
        "bz2file",
        "opencc-python-reimplemented"
    ],
    entry_points={
        'console_scripts': ['wikiext=wikiext.main:main']
    },
    python_requires=">=3.0",
    zip_safe=False,
)
