# Perform a sequence of commands while waiting for temperature
# Copyright (C) 2023 Camrbidge Yang <camyang@csail.mit.edu>
#


class LoopUntilTemperature:

  def __init__(self, config):
    self.printer = config.get_printer()
    self.gcode = self.printer.lookup_object('gcode')
    self.gcode.register_command("LOOP_UNTIL_TEMPERATURE",
                                self.cmd_LOOP_UNTIL_TEMPERATURE,
                                desc=self.cmd_TEMPERATURE_LOOP_help)
    self.printer_heaters = self.printer.lookup_object('heaters')

  cmd_TEMPERATURE_LOOP_help = "Perform motion on the toolhead while waiting for temperature"

  def cmd_LOOP_UNTIL_TEMPERATURE(self, gcmd):
    """Perform a sequence of commands while waiting for a temperature."""
    sensor_name = gcmd.get('SENSOR')
    loop_commands = gcmd.get_string("LOOP_COMMAND").split('\n')
    if sensor_name not in self.printer_heaters.available_sensors:
      raise gcmd.error("Unknown sensor '%s'" % (sensor_name,))
    min_temp = gcmd.get_float('MINIMUM', float('-inf'))
    max_temp = gcmd.get_float('MAXIMUM', float('inf'), above=min_temp)
    if min_temp == float('-inf') and max_temp == float('inf'):
      raise gcmd.error(
          "Error on 'TEMPERATURE_WAIT': missing MINIMUM or MAXIMUM.")
    if self.printer.get_start_args().get('debugoutput') is not None:
      return
    if sensor_name in self.printer_heaters.heaters:
      sensor = self.printer_heaters.heaters[sensor_name]
    else:
      sensor = self.printer.lookup_object(sensor_name)
    reactor = self.printer.get_reactor()
    eventtime = reactor.monotonic()
    toolhead = self.printer.lookup_object('toolhead')
    i = 0
    while not self.printer.is_shutdown():
      temp, _ = sensor.get_temp(eventtime)
      if temp >= min_temp and temp <= max_temp:
        return
      gcmd.respond_raw(self.printer_heaters._get_temp(eventtime))
      toolhead.wait_moves()
      self.gcode.run_script_from_command(loop_commands[i])
      i = (i + 1) % len(loop_commands)


def load_config(config):
  return LoopUntilTemperature(config)
