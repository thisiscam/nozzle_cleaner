#!/bin/bash

if [ ${UID} == '0' ]; then
    echo -e "Don't run this script as root! - aborting ..."
    exit 1
fi

if [ ! -d ~/klipper ]; then
   echo -e "Klipper must be installed on your system - aborting ..."
   exit 1
else
   echo "Klipper detected - let's go ..."
fi

if [ ! -d ~/nozzle_wipe ]; then
   echo -e "nozzle_wipe is missing - aborting ..."
   exit 1
else
   echo -e "nozzle_wipe - let's go ..."
   rm -f ~/klipper/klippy/extras/nozzle_wipe.py 2>&1>/dev/null
   ln -s ~/nozzle_wipe/nozzle_wipe.py ~/klipper/klippy/extras/nozzle_wipe.py
   sudo /bin/sh -c "cat > /etc/systemd/system/nozzle_wipe.service" << EOF
[Unit]
Description=Dummy Service for nozzle_wipe plugin
After=klipper.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/sleep 1
ExecStartPost=/usr/sbin/service klipper restart
[Install]
WantedBy=multi-user.target
EOF
   sudo systemctl daemon-reload
   sudo systemctl enable nozzle_wipe
   sudo systemctl restart nozzle_wipe
   echo -e "done."
fi

exit 0