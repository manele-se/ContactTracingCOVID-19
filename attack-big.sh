# Start a server and four clients
# Requires tmux
# Install tmux on Mac:
# brew install tmux

rm healthCareDataBase.txt
touch healthCareDataBase.txt

export PYTHONPATH=./:./server/src/
tmux new-session -d 'python3 server/src/server.py server/src/wwwroot'

export PYTHONPATH=./:./client/src/
tmux split-window -h -l 75% 'python3 client/src/client.py 40'
tmux split-window -v -l 50% 'python3 client/src/mallory.py 10'
open 'http://localhost:8008'
tmux -2 attach-session -d
