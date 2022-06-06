import setuptools


setuptools.setup(
    name="leankernel",
    version="0.0.1",
    author="Miguel Angel Marco Buzunariz",
    author_email="mmarco@unizar.es",
    description="Jupyter kernel for lean",
    url="https://github.com/miguelmarco/leankernel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    install_requires=[
        'ipykernel',
        'pexpect',
        ],
    python_requires='>=3.6',
)

