#!/bin/sh
# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA



# This script generate umit package to ubuntu from trunk

############ Deps: svn, dpkg-dev, dpkg-buildpackage, wget


###################
# We are at trunk directory
####################

# Generate tarball
python setup.py sdist



# Extract tarball
cd dist
tar zvxf umit*.tar.gz > extract.log
cd umit*



## Copy debian rules

cp -R ../../install_scripts/ubuntu/debian .

## Generate package:

sudo dpkg-buildpackage

cd ..
cd ../../
echo "########## FINISHED - Package was created ! ################"


