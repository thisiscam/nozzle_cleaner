# Perform a nozzle wipe at the X-gantry
# Copyright (C) 2023 Camrbidge Yang <camyang@csail.mit.edu>
#
#


class PurgeWipeNozzle:

  def __init__(self, config):
    self.printer = config.get_printer()
    nozzle_diameter = config.getsection("extruder").getfloat("nozzle_diameter")
    self.purge_line_dist = config.getfloat('purge_line_dist',
                                           default=nozzle_diameter * 15 / 0.4,
                                           above=0)
    max_x = config.getsection('stepper_x').getfloat('position_max',
                                                    note_valid=False)
    self.purge_loc_x = config.getfloat('purge_loc_x', default=max_x)
    self.wiper_loc_x = config.getfloat('wiper_pos_x')
    self.wiping_dist_x = config.getfloat('wiping_dist_x', above=0)
    self.max_repeat = config.getint('max_repeat', default=3, minval=1)
    self.travel_speed = config.getfloat('travel_speed', default=100, above=0)
    self.wipe_speed = config.getfloat('wipe_speed', default=20, above=0)

    self.gcode = self.printer.lookup_object('gcode')
    self.gcode_move = self.printer.lookup_object('gcode_move')

    self.gcode.register_command("WIPE_NOZZLE",
                                self.cmd_WIPE_NOZZLE,
                                desc=self.cmd_WIPE_NOZZLE_help)

  cmd_WIPE_NOZZLE_help = "Wipe the nozzle at the X-gantry"

  def cmd_WIPE_NOZZLE(self, gcmd):
    # check if all axes are homed
    toolhead = self.printer.lookup_object('toolhead')
    curtime = self.printer.get_reactor().monotonic()
    kin_status = toolhead.get_kinematics().get_status(curtime)

    if 'x' not in kin_status['homed_axes']:
      raise gcmd.error("You must home X axis first")

    gcmd.respond_info("PurgeWipeNozzle: start wiping nozzle ...")

    # Move to center of the wiper
    toolhead.manual_move([self.wiper_loc_x], self.travel_speed)

    # try to get the current nozzle temperature
    temperature = self.printer.lookup_object('heater').lookup_object(
        'extruder').temperature
    gcmd.respond_info("PurgeWipeNozzle: nozzle temperature is {temp}".format(
        temp=temperature))


def load_config(config):
  return PurgeWipeNozzle(config)
