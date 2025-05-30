# this should install all these modules into ../../sitepackages/gpib and
# make a gpib.pth file
# the extra_path make a .pth file - careful here the manual says
# i should used install_path

from distutils.core import setup
#print dir(install)
setup(name="gpib3", packages=[''], extra_path=['gpib3'])
