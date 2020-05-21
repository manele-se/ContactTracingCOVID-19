# Start a server, 40 normal users and 20 malicious collectors
# Requires tmux
# Install tmux on Mac:
# brew install tmux

rm healthCareDataBase.txt
touch healthCareDataBase.txt

export PYTHONPATH=./:./server/src/
tmux new-session -d 'python3 server/src/server.py server/src/wwwroot'

export PYTHONPATH=./:./client/src/
tmux split-window -h -l 75% 'python3 apps/src/app.py 40'
tmux split-window -v -l 50% 'python3 apps/src/malloryCollector.py 20'
open 'http://localhost:8008'
tmux -2 attach-session -d
