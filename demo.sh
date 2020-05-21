# Start a server and four clients
# Requires tmux
# Install tmux on Mac: brew install tmux
# Install tmux on Ubuntu: apt-get install tmux

# Requires python3.7 or later, and python modules pycrypto and tornado
# Install: pip3 install pycrypto tornado

rm healthCareDataBase.txt
touch healthCareDataBase.txt

export PYTHONPATH=./:./server/src/
tmux new-session -d 'python3 server/src/server.py server/src/wwwroot'

export PYTHONPATH=./:./apps/src/
tmux split-window -h -p 75 'python3 apps/src/app.py Alice'
tmux split-window -v -p 75 'python3 apps/src/app.py Bob'
tmux split-window -v -p 67 'python3 apps/src/app.py Carol'
tmux split-window -v -p 50 'python3 apps/src/app.py Dave'
open 'http://localhost:8008'
tmux -2 attach-session -d
