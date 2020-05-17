# Start a server and four clients
# Requires tmux
# Install tmux on Mac:
# brew install tmux

rm healthCareDataBase.txt
touch healthCareDataBase.txt

export PYTHONPATH=./:./server/src/
tmux new-session -d 'python3 server/src/server.py server/src/wwwroot'

export PYTHONPATH=./:./apps/src/
tmux split-window -h -l 75% 'python3 apps/src/app.py Alice'
tmux split-window -v -l 75% 'python3 apps/src/app.py Bob'
tmux split-window -v -l 67% 'python3 apps/src/app.py Carol'
tmux split-window -v -l 50% 'python3 apps/src/mallory.py Mallory'
open 'http://localhost:8008'
tmux -2 attach-session -d
