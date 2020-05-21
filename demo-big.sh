# Start a server and 40 clients

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
tmux split-window -h -p 75 'python3 apps/src/app.py 40'

open 'http://localhost:8008'
tmux -2 attach-session -d
