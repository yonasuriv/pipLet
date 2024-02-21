#!/bin/bash

BLUE='\033[94m'
RED='\033[91m'
GREEN='\033[92m'
ORANGE='\033[93m'
RESET='\e[0m'

printf"$RED                                        $RESET"
printf"$CYAN       .__       .____           __    $RESET"
printf"$CYAN ______ |__|_____ |    |    _____/  |_  $RESET"
printf"$CYAN |____ \|  \____ \|    |  _/ __ \   __\ $RESET"
printf"$CYAN |  |_> >  |  |_> >    |__\  ___/|  |   $RESET"
printf"$CYAN |   __/|__|   __/|_______ \___  >__|   $RESET"
printf"$CYAN |__|      |__|           \/   \/ $RESET"     github.com/yonasuriv
echo ""

if [[ $EUID -ne 0 ]]; then
   echo
   printf"$RED[!]$RESET To install this script, you must run it as root. Use$RED python piplet.py$RESET otherwise."
   exit 1
fi

sudo mv piplet.py /usr/bin/piplet
sudo chmod +x /usr/bin/piplet
#cd ..
#rm -rf pipLet

printf"$OKGREEN[*]$RESET pipLet successfully installed. Type$RED piplet$RESET in your terminal to get started."