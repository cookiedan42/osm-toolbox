import setuptools

# might have to change the name ><
projectName = "osm_toolbox"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osm_toolbox",
    version="0.0.2",
    author="Daniel Tan",
    author_email="r@ecookiedan42.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        projectName,
        projectName+".geojson2",
        projectName+".sg_govt",
        projectName+".transformers",
        projectName+".osm_pbf",
        ],
    python_requires=">=3.6",
    install_requires=["shapely","osmium","pyproj >=3.1.0"]
)