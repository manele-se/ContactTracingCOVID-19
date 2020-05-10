# Start a server and 50 clients
# Requires tmux
# Install tmux on Mac:
# brew install tmux
export PYTHONPATH=./:./server/src/
tmux new-session -d 'python3 server/src/server.py server/src/wwwroot'

export PYTHONPATH=./:./client/src/
tmux split-window -h -l 75% 'python3 client/src/client.py 20'

open 'http://localhost:8008'
tmux -2 attach-session -d
