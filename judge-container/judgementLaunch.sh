timeout -s 9 450s docker build --network host -t judgement:latest ./judgement > verdict.temp
if [ ! $? -eq 0 ]  ; then
	echo BE
	exit
fi
timeout -s 9 450s docker run judgement bash judge.sh $1 $2 $3 $4 > verdict.temp
if [ ! $? -eq 0 ]  ; then
	echo JE
	exit
fi
echo AC
