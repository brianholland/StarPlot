from setuptools import setup

setup(name='StarPlot',
      version='0.1',
      description='Plot of nearby stars',
      url='https://gitlab.bdholland.com/Brian/StarPlot',
      author='Brian D. Holland',
      author_email='brian.d.holland@gmail.com',
      license='MIT',
      packages=['StarPlot'],
      install_requires=[
          'requests', 'pandas', 'matplotlib', 'numpy', 'bs4', 'mpl_toolkits'
       ], 
      zip_safe=False)
