from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='walter',
      version='0.1',
      description='Walter is a Project Manager',
      url='http://github.com/Tahapy/Walter',
      author='Mohammad Taha (TahaPY)',
      author_email='taha@cerberusteam.ir',
      license='MIT',
      packages=['walter'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      python_requires='>=3.6',
      install_requires=["tabulate", "virtualenv"],
      dependency_links=[
          'https://github.com/tahapy/CharonDB/tarball/master'],
      entry_points='''
        [console_scripts]
        walter=walter.app:main
        ''',
      )
