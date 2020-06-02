# Contact Tracing Application for COVID-19

This is a project aiming at simulating the DP-3T protocol,  https://github.com/DP-3T/documents/blob/master/DP3T%20White%20Paper.pdf, with focus on
privacy protection.

## Disclamer
This project has been completed on the 24th of May. Every changes in the protocol happened after that date are not taken into consideration. 

## Instructions to run the simulation

Requirements to run the simulation:

 - Python 3.7 or later, preferably Python 3.8
 - Tornado library must be installed: `pip install tornado`
 - PyCrypto library must be installed: `pip install pycrypto`

Before running, please edit the file `server/src/wwwroot/index.html` and replace the `GOOGLE_MAPS_API_KEY` string with your own Google Maps API key.

### MacOS and Linux

On MacOS and Linux, **tmux** is also required for running multiple terminal sessions in the same window.

 - On MacOS, install tmux using: `brew install tmux`
 - On Ubuntu Linux, install tmux using: `apt-get install tmux`

### Windows 10

On a Windows 10 computer with Windows Subsystem for Linux 2 (WSL2), the instructions for running the simulation is the same as for Linux, as seen above. For Windows 10 computers without WSL2, there are three PowerShell scripts provided, and it is required to install Python 3.7 or later and make it the default Python interpreter. Also, installing the PyCrypto library on Windows 10 requires some extra steps:

 - First download and install Microsoft Visual C++ Build Tools v14.0 (VS2015)
 - Start a Developer Command Prompt for VS2015
 - Install PyCrypto using these commands:

```
set CL=-FI"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include\stdint.h"
pip install pycrypto
```

Running non-signed scripts in PowerShell requires you to set a permissive execution policy. Before running any of the scripts below, start PowerShell and run:

```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass
```

## Simulation of the DP-3T protocol

To run the simulation, 2 shell scripts have been added. One, demo.sh, simulates the scenario with 4 devices, Alice, Bob, Carol and Dave. From a command line on MacOS or Linux, type:

```
./demo.sh
```

When running simulations in Linux, you need to open a web browser manually and enter the address `http://localhost:8008/`

To run the simulation in Windows, type:

```
.\demo.ps1
```

To have a better understanding of the protocol, another simulation scenario has been created. This can be activated by running the script which creates 40 devices. On MacOS or Linux, type:

```
./ demo-big.sh
```

To run the simulation in Windows, type:

```
.\demo-big.ps1
```

## Simulation of the attack

To run the attack, a third shellscript called location-trail-attack.sh had been added. The script runs on MacOS and Linux by typing:

```
./location-trail-attack.sh
```

To run the attack in Windows, type:

```
.\location-trail-attack.ps1
```

In this case 20 malicious devices are created together with 40 normal users. 

## Simulation video

For a demonstration of this project, please see https://vimeo.com/elenamarzi/dp3t-simulation
