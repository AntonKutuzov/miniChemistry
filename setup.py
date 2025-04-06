from setuptools import setup, find_packages

setup(
    name="minichemistry",
    version="0.0.9",
    author="Antons Kutuzovs",
    author_email="akutuzovsssss@gmail.com",
    description="A package to model simple stoichiometric calculations over chemical reactions",
    long_description=open("miniChemistry/README.md").read(),  # Include the content of README.md
    long_description_content_type="text/markdown",  # Format of README.md (Markdown)
    url="https://github.com/AntonKutuzov/miniChemistry",  # Replace with your GitHub repo URL
    packages=find_packages(),  # Automatically find all packages in your project
    install_requires=['chemparse', 'sympy', 'pandas', 'Pint', 'typeguard'],
    include_package_data=True,
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
