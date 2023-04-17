# Perform a nozzle wipe with a temperature wait
# Copyright (C) 2023 Camrbidge Yang <camyang@csail.mit.edu>
#


class WipeNozzle:

  def __init__(self, config):
    self.printer = config.get_printer()

    self.gcode = self.printer.lookup_object('gcode')

    self.gcode.register_command("WIPE_NOZZLE",
                                self.cmd_WIPE_NOZZLE,
                                desc=self.cmd_WIPE_NOZZLE_help)

  cmd_WIPE_NOZZLE_help = "Perform a wiping motion on the toolhead, optionally waits for the temperature to drop"

  def cmd_WIPE_NOZZLE(self, gcmd):
    nozzle_standby_temperature = gcmd.get_float("NOZZLE_STANDBY_TEMPERATURE",
                                                None)
    num_wipes = gcmd.get_int("NUM_WIPES", 10)
    wipe_dist_x = gcmd.get_float("WIPE_DIST_X", minval=0, default=0)
    wipe_dist_y = gcmd.get_float("WIPE_DIST_Y", minval=0, default=0)
    wipe_speed = gcmd.get_float("WIPE_SPEED", minval=50, default=0)

    toolhead = self.printer.lookup_object('toolhead')
    curtime = self.printer.get_reactor().monotonic()
    kin_status = toolhead.get_kinematics().get_status(curtime)

    # Make sure X, Y are homed
    if ('x' not in kin_status['homed_axes'] or
        'y' not in kin_status['homed_axes']):
      raise gcmd.error("You must home X and Y axes first")

    gcmd.respond_info("NozzleWipe: start wiping ...")

    x_loc, y_loc, *_ = toolhead.get_position()

    def do_wipe_motion():
      for direction in (-1, 1):
        toolhead.manual_move([
            x_loc + direction * wipe_dist_x / 2,
            y_loc + direction * wipe_dist_y / 2,
        ], wipe_speed)

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
