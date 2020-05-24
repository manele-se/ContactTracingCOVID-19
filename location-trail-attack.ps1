# Start a server, 40 normal users and 20 malicious collectors, in PowerShell

# Requires python3.7 or later, and python modules pycrypto and tornado
# Install: pip install pycrypto tornado

# Installing pycrypto might require you to:
#  - First install Microsoft Visual C++ Build Tools v14.0 (VS2015)
#  - Start a Developer Command Prompt for VS2015
#  - Install pycrypto using these steps:
#      set CL=-FI"C:\Program Files (x86)\Microsoft Visual Studo 14.0\VC\include\stdint.h"
#      pip install pycrypto

# To start this script, first set the execution policy to Bypass
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass

$env:PYTHONPATH = ".\;.\server\src\;.\apps\src\"

# Start the simulation server
Start-Process python -ArgumentList ".\server\src\server.py", ".\server\src\wwwroot\"

# Start 40 clients
Start-Process python -ArgumentList ".\apps\src\app.py", "40"

# Start 20 malicious collectors
Start-Process python -ArgumentList ".\apps\src\malloryCollector.py", "20"

# Open the observation interface in the default web browser

Start-Process 'http://localhost:8008/'
