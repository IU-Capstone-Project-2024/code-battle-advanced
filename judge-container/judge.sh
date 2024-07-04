#!/bin/bash

code=$1
task=$2
compiler=$3
mstime=$4
numberOfFiles=$(ls -1 ./tasks/$task/tests| wc -l)

if [ ! -e "./tasks/$2/checker.sh" ]
then
	>&2 echo There is no checker.sh to check the solutions
	exit -1
fi

if [ "$compiler" = "cpp" ]; then 
	g++ -x c++ $code -o compiledCode
	exitCode=$?
	if [ ! $exitCode -eq 0 ]  ; then
		echo CE 0 0
		exit
	fi
fi

if [ "$compiler" = "java" ]; then
	javac -d "$PWD" $code
	exitCode=$?
	if [ ! $exitCode -eq 0 ]  ; then
		echo CE 0 0
		exit
	fi
	compiledClass=${code##*/}
	compiledClass=${compiledClass%?????}
fi

for fileId in $(seq 0 $(($numberOfFiles - 1))) 
do
	file="./tasks/${task}/tests/${fileId}.in"
	if [ -f "$file" ]; then
		if [ "$compiler" = "python3" ]; then 
			cat $file | timeout -s 9 $(echo $mstime / 1000 | bc -l)s python3 -I $code > temp.out
			exitCode=$?
		else if [ "$compiler" = "cpp" ]; then 
			cat $file | timeout -s 9 $(echo $mstime / 1000 | bc -l)s ./compiledCode > temp.out
			exitCode=$?
		else if [ "$compiler" = "java" ]; then 
			cat $file | timeout -s 9 $(echo $mstime / 1000 | bc -l)s java $compiledClass > temp.out
			exitCode=$?
		else
			>&2 echo Unsupported compiler option
			exit
		fi fi fi # Cool way to see the number of compilers
		
		
		if [ $exitCode -eq 137 ]  ; then
			echo TL $fileId 0
		else if [ $exitCode -eq 124 ]  ; then
			echo TL $fileId 0
		else if [ ! $exitCode -eq 0 ]  ; then
			echo RE $fileId 0
		else if [ ! $(sh ./tasks/$task/checker.sh $file temp.out) = "True" ] ; then
			echo WA $fileId 0
		else
			echo AC $fileId 1
		fi fi fi fi
		rm temp.out
	fi
done
	
	
if [ "$compiler" = "java" ]; then
	rm $compiledClass.class
fi
# echo AC
exit

