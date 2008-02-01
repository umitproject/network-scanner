#!/bin/sh


# https://sourceforge.net/tracker/?func=detail&atid=752647&aid=1846955&group_id=142490
echo
echo "####################################"
echo "# Umit Dependencies - Verify    "
echo "####################################"
echo

#Func check 
Check(){

if [ -z "$1" ] ; then 
  exit 0 
fi 

if [ $? = 0 ]; then
  echo "## $1  -- checked "
else 
   echo "## $1  -- unchecked " 
fi 
}

# Python Checking
python --version 1>/dev/null 2>&1
Check "Python"

# PyGTK Checking 
python -c "import gtk"
Check "PyGTK"

# sqllite
pythonn -c 
Check "SQLite"



