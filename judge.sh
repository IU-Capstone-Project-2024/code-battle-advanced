#!/bin/bash

code=$1
task=$2
compiler=$3
mstime=$4
numberOfFiles=$(ls -1 $task/tests| wc -l)
if [ ! -e "$2/checker.sh" ]
then
 >&2 echo There is no checker.sh to check the solutions
 exit
fi

if [ "$compiler" = "python3" ]
then
 for fileId in $(seq 0 $(($numberOfFiles - 1))) 
 do
  file="${task}/tests/${fileId}.in"
  if [ -f "$file" ]; then
   cat $file | timeout -s 9 $(echo $mstime / 1000 | bc -l)s python3 -I $code > temp.out
   exitCode=$?
   if [ $exitCode -eq 137 ]  ; then
    echo TL $fileId
    exit
   fi
   if [ $exitCode -eq 124 ]  ; then
    echo TL $fileId
    exit
   fi
   if [ ! $exitCode -eq 0 ]  ; then
    echo RE $fileId
    exit
   fi
   if [ $(sh $task/checker.sh $file temp.out) = "False" ] ; then
    echo WA $fileId
    exit
   fi
   rm temp.out
  fi
 done
 
 echo AC
fi
