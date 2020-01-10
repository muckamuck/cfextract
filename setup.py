from setuptools import setup
setup(
    name="CFExtract",
    version='0.1.0',
    packages=['cfextract'],
    description='Extract Stackility/CloudFormation files',
    author='Chuck Muckamuck',
    author_email='Chuck.Muckamuck@gmail.com',
    install_requires=[
        "boto3>=1.9",
        "Click>=7"
    ],
    entry_points="""
        [console_scripts]
        cfextract=cfextract.command:cli
    """
)
