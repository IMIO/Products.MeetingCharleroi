from setuptools import setup, find_packages
import os

version = '4.1.dev0'

setup(name='Products.MeetingCharleroi',
      version=version,
      description="Official meetings management for college and council "
      "of Charleroi city (PloneMeeting extension profile)",
      long_description=open("README.txt").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=["Programming Language :: Python"],
      keywords='',
      author='',
      author_email='',
      url='http://www.imio.be/produits/gestion-des-deliberations',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=['unittest2',
                'zope.testing',
                'plone.testing',
                'plone.app.testing',
                'plone.app.robotframework',
                'Products.CMFPlacefulWorkflow',
                'zope.testing',
                'Products.PloneTestCase'],
          templates=['Genshi', ]),
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'Pillow',
          'Products.PloneMeeting',
          'Products.MeetingCommunes'],
      entry_points={},
      )
