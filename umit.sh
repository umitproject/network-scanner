#!/bin/sh


if [ -z $1 ] 
then
    echo "NO argument is Given : e.g. deps , umit , run "
    
elif [ $1 = "deps" ]
then
	############ Make Deps ##################
	cd deps/clann/
	make

	cd ../../

	cd deps/libkeybinder/ 
	make

	cd ../../
	##############################################

	cd deps

	####### Copy The clann in umit/ ############


	find ./clann -type d -name '*' -exec mkdir -p ../umit/{} \;
	find ./clann -type f -name '*' -exec cp {} ../umit/{} \;


	####### Copy The libkeybinder in umit/ ############


	find ./libkeybinder -type d -name '*' -exec mkdir -p ../umit/{} \;
	find ./libkeybinder -type f -name '*' -exec cp {} ../umit/{} \;

	cd ..

	svn checkout http://pypcap.googlecode.com/svn/trunk/ pypcap-read-only
	cd pypcap-read-only
	make
	sudo make install 

	cd..

	##############################################################
	

	
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

