from setuptools import setup, find_packages

version = '4.1rc7.dev0'

setup(name='Products.MeetingCharleroi',
      version=version,
      description="Official meetings management for college and council "
      "of Charleroi city (PloneMeeting extension profile)",
      long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
      classifiers=["Programming Language :: Python"],
      keywords='plone official meetings management egov communesplone imio plonegov charleroi',
      author='Gauthier Bastien',
      author_email='gauthier@imio.be',
      url='http://www.imio.be/produits/gestion-des-deliberations',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=['Products.PloneMeeting[test]'],
          templates=['Genshi', ]),
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'Pillow',
          'Products.MeetingCommunes'],
      entry_points={},
      )
