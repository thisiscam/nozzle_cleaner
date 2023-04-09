# Perform a nozzle wipe at the X-gantry
# Copyright (C) 2023 Camrbidge Yang <camyang@csail.mit.edu>
#
#


class WipeNozzle:

  def __init__(self, config):
    self.printer = config.get_printer()

    self.wiper_loc_x = config.getfloat('wiper_loc_x')
    self.wiping_dist_x = config.getfloat('wiping_dist_x', above=0)

    self.travel_speed = config.getfloat('travel_speed', default=100, above=0)
    self.wipe_speed = config.getfloat('wipe_speed', default=50, above=0)

    self.gcode = self.printer.lookup_object('gcode')

    self.gcode.register_command("WIPE_NOZZLE",
                                self.cmd_WIPE_NOZZLE,
                                desc=self.cmd_WIPE_NOZZLE_help)

  cmd_WIPE_NOZZLE_help = "Wipe the nozzle at the X-gantry"

  def cmd_WIPE_NOZZLE(self, gcmd):
    nozzle_standby_temperature = gcmd.get_float("NOZZLE_STANDBY_TEMPERATURE",
                                                None)
    num_wipes = gcmd.get_int("NUM_WIPES", 10)

    # check if all axes are homed
    toolhead = self.printer.lookup_object('toolhead')
    curtime = self.printer.get_reactor().monotonic()
    kin_status = toolhead.get_kinematics().get_status(curtime)

    if 'x' not in kin_status['homed_axes']:
      raise gcmd.error("You must home X axis first")

    gcmd.respond_info("NozzleWipe: start wiping ...")

    # Move to center of the wiper
    toolhead.manual_move([self.wiper_loc_x], self.travel_speed)

    def do_wipe_motion():
      for direction in (-1, 1):
        toolhead.manual_move(
            [self.wiper_loc_x + direction * self.wiping_dist_x / 2],
            self.wipe_speed)

    if nozzle_standby_temperature is not None:
      extruder_heater = self.printer.lookup_object('extruder').get_heater()
      extruder_heater.alter_target(nozzle_standby_temperature)
      gcmd.respond_info(
          "NozzleWipe: wiping while waiting for temperature to drop ...")
      while True:
        curtime = self.printer.get_reactor().monotonic()
        temperature, _ = extruder_heater.get_temp(curtime)
        if temperature <= nozzle_standby_temperature:
          break
        toolhead.wait_moves()
        do_wipe_motion()

    for _ in range(num_wipes):
      do_wipe_motion()
    toolhead.wait_moves()

    gcmd.respond_info("NozzleWipe: done!")


def load_config(config):
  return WipeNozzle(config)
