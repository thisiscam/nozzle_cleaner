# Overview

This Python host module provides a simple solution for automatically wiping a 3D printer's nozzle. It continues wiping until the nozzle reaches a specified target temperature, avoiding the need for klipper macros.

# WARNING

This repo contains Python code that can manipulate your printer!  
If you are not sure what you are doing, do not use this!!!
I am not responsible for any consequence caused by this script.

# Installation

To install as a moonraker service, follow these steps:

```bash
./install
```

To uninstall:

```
bash
./install -u
```

Next, update your printer.cfg file with the following configuration:

```
[wipe_nozzle]
wiper_loc_x = 247.5 # center of the wiper/brush
wiping_dist_x = 20 # horizontal wiping distance (around the width of the brush + 2mm)
travel_speed = 100 # speed to move to the wiper location
wipe_speed = 60 # wiping speed in mm/s
```

# How to Use

After installation, the `WIPE_NOZZLE` command becomes available. The command accepts two parameters: `NUM_WIPES` and `NOZZLE_STANDBY_TEMPERATURE`.

If `NOZZLE_STANDBY_TEMPERATURE` is provided, the command will wipe until the extruder heater's temperature drops to this value, followed by `NUM_WIPES` of additional wipes.
If `NOZZLE_STANDBY_TEMPERATURE` is not provided, the command will perform `NUM_WIPES` of wipes without waiting for the temperature.


Further, I have a simple purge macro that makes use of `WIPE_NOZZLE` in `purge_wipe.cfg`.
Please feel free to adapt this to your use case!

# Limitations

Currently, only fixed x-gantry mounted wipers (typically found on bed-slinger printers) are supported. However, extending support to other mount types should be relatively simple.

The script relies on waits for wiping moves to finish then checks the temperature --- this causes the printer to "pause" slightly in between wiping moves. I found this behavior to not be a problem for me. 

# Acknowledgements

This code is heavily inspired by other klipper extensions:

- https://github.com/protoloft/klipper_z_calibration
- https://github.com/julianschill/klipper-led_effect