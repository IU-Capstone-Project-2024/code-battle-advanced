curl -vL -c "cookies.txt" -d username=Tedor -d password=lol http://192.168.49.2:32001/signin -o signin.html
#curl -b "cookies.txt" http://192.168.49.2:32001/contest/668add705bf7fb697d58f013/task/668addab5bf7fb697d58f014 -o contest.html

url="http://192.168.49.2:32001/create"
name="Calculator contest"
stime="16/07/2024 12:17:00"
duration="36000"
description="Big description"
location="@../contest-container/calc_module.py"

curl $url -X POST -b "cookies.txt" -F "type_python=$location" -F "ContestName=$name" -F "duration=$duration" -F "StartTime=$stime" -F "description=$description" -o create.html

