#!/bin/sh


if [ -z $1 ] 
then
    echo "NO argument is Given : e.g. deps , umit , run "
    
elif [ $1 = "deps" ]
then
    # Update & Install & Copy Submodules ------------------#

    # Initialize all submodules ; 
    # zion, clann, pypcap, libkeybinder, umpa, umit-common  

    git submodule update --init

    cd deps

    # clann -------------------------------------------#

    cd clann
    git checkout origin/origin/clann
    make

    cd ..

    # copy clann in umit/
    find ./clann -type d -name '*' -exec mkdir -p ../umit/{} \;
    find ./clann -type f -name '*' -exec cp {} ../umit/{} \;

    # libkeybinder ------------------------------------#

    cd libkeybinder/ 
    make
    
    cd .. 

    # copy libkeybinder in umit/
    find ./libkeybinder -type d -name '*' -exec mkdir -p ../umit/{} \;
    find ./libkeybinder -type f -name '*' -exec cp {} ../umit/{} \;

    # umpa --------------------------------------------#
    
    cd umpa/
    python setup.py install

    cd ..

    # pypcap ------------------------------------------#

    cd pypcap
    make
    sudo make install 

    cd ..

    # -------------------------------------------------#
    
elif [ $1 = "umit" ]
then
    sudo python bin/umit
elif [ $1 = "run" ]
then
    ./umit.sh deps
    ./umit.sh umit

else
    echo "Enter correct arg : deps, umit , run"
fi

