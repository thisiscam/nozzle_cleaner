#!/bin/bash

if [ ${UID} == '0' ]; then
    echo -e "Don't run this script as root! - aborting ..."
    exit 1
fi

if [ ! -d ~/klipper ]; then
   echo "Klipper must be installed on your system - aborting ..."
   exit 1
else
   echo "Klipper detected - let's go ..."
fi

echo "nozzle_wipe - let's go ..."
rm -f ~/klipper/klippy/extras/nozzle_wipe.py 2>&1 > /dev/null
sudo systemctl disable nozzle_wipe
rm -f /etc/systemd/system/nozzle_wipe.service 2>&1 > /dev/null
sudo systemctl daemon-reload
echo "done."
