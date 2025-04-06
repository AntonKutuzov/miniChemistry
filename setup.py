from setuptools import setup, find_packages

setup(
    name="minichemistry",
    version="0.0.9",
    author="Antons Kutuzovs",
    author_email="akutuzovsssss@gmail.com",
    description="A package to model simple stoichiometric calculations over chemical reactions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AntonKutuzov/miniChemistry",
    packages=find_packages(),
    install_requires=['chemparse', 'sympy', 'pandas', 'Pint', 'typeguard', 'openpyxl'],
    include_package_data=True,
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
