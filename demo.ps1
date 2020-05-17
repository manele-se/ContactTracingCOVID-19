$serversession = New-PSSession

# Use Invoke-Command to start

# $env:PYTHONPATH = ".\;.\server\src\"
# python .\server\src\server.py .\server\src\wwwroot\

$alicesession = New-PSSession
# $env:PYTHONPATH = ".\;.\apps\src\"
# python .\apps\src\app.py Alice

$bobsession = New-PSSession
# $env:PYTHONPATH = ".\;.\apps\src\"
# python .\apps\src\app.py Bob

# ...