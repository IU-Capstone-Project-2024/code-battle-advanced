cd ..
mkdir mirror

git clone --bare git@gitlab.pg.innopolis.university:f.smirnov/code-battle-advanced.git mirror
cd mirror
git push --mirror git@github.com:IU-Capstone-Project-2024/code-battle-advanced.git

cd ..
rm -rf mirror

