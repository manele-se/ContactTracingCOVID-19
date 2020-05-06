cd server/src
python3 server.py &
cd ../..
cd client/src
python3 client.py 1 &
python3 client.py 2 &
python3 client.py 3 &
python3 client.py 4 &
