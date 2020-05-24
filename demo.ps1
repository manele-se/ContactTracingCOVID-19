# Start a server and four clients

# Requires PowerShell

# Requires python3.7 or later, and python modules pycrypto and tornado
# Install: pip install pycrypto tornado
# Installing pycrypto might require you to also install Microsoft Visual C++ Build Tools v14.0

# To start this script, first set the execution policy to Bypass
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass

# Start the simulation server

$env:PYTHONPATH = ".\;.\server\src\"
$serversession = New-PSSession
Invoke-Command -Session $serversession -Scriptblock {python .\server\src\server.py .\server\src\wwwroot\}

# Start four clients, Alice, Bob, Carol and Dave

$env:PYTHONPATH = ".\;.\apps\src\"
$alicesession = New-PSSession
Invoke-Command -Session $alicesession -Scriptblock {python .\apps\src\app.py Alice}

$bobsession = New-PSSession
Invoke-Command -Session $bobsession -Scriptblock {python .\apps\src\app.py Bob}

$carolsession = New-PSSession
Invoke-Command -Session $carolsession -Scriptblock {python .\apps\src\app.py Carol}

$davesession = New-PSSession
Invoke-Command -Session $davesession -Scriptblock {python .\apps\src\app.py Dave}

# Open the observation interface in the default web browser

Start 'http://localhost:8008/'
