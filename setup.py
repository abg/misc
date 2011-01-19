from distutils.core import setup
from config4py import __version__ as version

extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
        use_2to3_fixers=[]
    )

setup(name='Config4Py',
      version=version,
      description='Configuration Utility for Python',
      author='Andrew Garner',
      author_email='muzazzi@gmail.com',
      url='http://github.com/abg/config4py',
      packages=['config4py'],
      **extra
)
