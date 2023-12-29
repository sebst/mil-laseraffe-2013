import logging
from typing import Dict
from typing import Optional
import time

import mcs

log = logging.getLogger(__name__)

PORT_ACTUALIZE_TIME = 0.1


class Plunger(mcs.HardwareDevice):
    """Module which is used as a pipette.

    Pick and dispense liquid with pipette tip.
    Position requests need to be multiplied with -1.
    The plunger can use the small chamber or both small and big chamber
    depending on the magnet valve state (on/off). Steps given refer either to
    the small chamber alone if valve is off or to both if valve is on.

    Note: not all possible mcs commands need to be used, therefore the
    methods here leave out stop command.
    """

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }

    BIG_CHAMBER = 5513
    SMALL_CHAMBER = 770
    TOTAL_STEPS = 6400

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        """For now assume same behaviour as for pipette head regarding init"""

        self.reset()
        self.init()

        # move out- and inside light barrier to get same physical position as
        # starting point
        if self.is_in_light_barrier() == 0:
            self.set_port_mode(port=1, mode=2)
            self.move(position=8000, speed=4000, timeout=30, cmd_mode=2)

        self.init()  # do init again to set actual position to 0

    def _volume_to_steps(self, volume: int, small_chamber_only: bool = False)\
            -> int:
        """Calculate total steps for plunger to reach the desired volume.

        Args:
            volume: volume to pipette
            small_chamber_only: if True calculate the steps based on small
                                chamber, otherwise for both
        Returns:
            steps rounded and inverted
        """

        if small_chamber_only:
            total_volume = self.SMALL_CHAMBER
        else:
            total_volume = self.BIG_CHAMBER + self.SMALL_CHAMBER

        steps = self.TOTAL_STEPS / total_volume * volume

        return -round(steps)

    def steps_to_volume(self, position: int, small_chamber_only: bool = False)\
            -> int:
        """Calculate total volume of plunger based on position/steps.

        Args:
            position: current position in steps
            small_chamber_only: if True calculate the volume based on small
                                chamber, otherwise for both
        Returns:
            volume: steps translated fo volume
        """

        if small_chamber_only:
            total_volume = self.SMALL_CHAMBER
        else:
            total_volume = self.BIG_CHAMBER + self.SMALL_CHAMBER

        volume = position * total_volume / self.TOTAL_STEPS

        return int(volume)

    def move_to_volume(self, target_volume: int, speed: int, be_precise=False) \
            -> None:
        """Move to target volume to either take up or discard volume.

        Contains calculation of volume to steps.
        If you move to or within a volume that fits into the small chamber you
        can set be_precise. This ensures that only the small chamber is used,
        resulting in a more precise volume.

        Args:
            target_volume: volume for plunger to move to
            speed: speed for plunger move
            be_precise: tells if it shall be preferred to use the small chamber
                         only if possible
        """

        # calculation of current_volume helps to decide which chamber to use
        # IMPORTANT: if discarding volume, there can occur too little volume
        # outputs if this move uses be_precise = True but the volume was taken
        # up using both chambers (use_only_small_chamber was set to False
        # automatically depending on the target volume)
        current_plunger_pos = self.get_pos()
        current_volume = self.steps_to_volume(position=current_plunger_pos,
                                              small_chamber_only=be_precise)

        # check where we are and which chamber to use
        # this determines which valve to use
        use_only_small_chamber = False
        if target_volume < current_volume:
            # we want to discard a portion or whole volume
            if be_precise and current_volume <= self.SMALL_CHAMBER:
                use_only_small_chamber = True
        else:
            # we want to take up volume
            if be_precise and target_volume <= self.SMALL_CHAMBER:
                use_only_small_chamber = True

        if use_only_small_chamber:
            self.set_valve_off(1)
        else:
            self.set_valve_on(1)

        position = self._volume_to_steps(
            target_volume, use_only_small_chamber)

        self.move_abs(position=position, speed=speed, timeout=30)

    def get_pressure(self) -> int:
        return self.get_port(port=12, signed=True)

    def get_pressure_raw(self) -> int:
        return self.get_port(port=250)

    def is_in_light_barrier(self) -> bool:
        """Returns value for light barrier sensor.

        Value is inverted and is corrected here for better readability
        """

        return not bool(self.get_port(port=1))

    def set_valve_on(self, valve_nr: int) -> None:
        """Open magnetic valve.

        Args:
            valve_nr: valve of interest (0 or 1 for MC)
        """

        self.set_port(port=valve_nr+3, value=500, length=2,
                      pulse_time=50)
        time.sleep(5*PORT_ACTUALIZE_TIME)

    def set_valve_off(self, valve_nr: int) -> None:
        """Close magnetic valve.

        Args:
            valve_nr: valve of interest (0 or 1 for MC)
        """

        self.set_port(port=valve_nr+3, value=0, length=2,
                      pulse_time=0)
        time.sleep(5*PORT_ACTUALIZE_TIME)


class Ejector(mcs.HardwareDevice):
    """Module which is used as a pipette.

    It shall be able to pick and eject pipette tips.

    Note: not all possible mcs commands need to be used, therefore the
    methods here leave out the commands for rotate and stop  as well as port
    read outs for get gripper (duplicates get sensor - get
    sensor in was also removed as it is not relevant for this module).
    """

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }

    STD_EJ_SPEED = 1000
    STD_EJ_STEP = 1000

    # approximation of steps done in- or outside light barrier
    IN_LS = 1700  # steps that approximately can be done inside light barrier
    OUTSIDE_LS = 6500  # steps that can be done outside light barrier

    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)

    def startup(self) -> None:
        """Initializes the ejector of pipette head.

        If gripper is open it is closed.
        May include move into light barrier if not already there, because
        position 0 is defined as the one where the head hits the light barrier.

        We must drive in- and outside once to confirm correct position.
        """

        self.reset()
        self.init()  # init and gets gripper in

        # move into light barrier
        # typically the light barrier is reached by moving upwards
        steps = self.get_pos()  # should be 0
        step_size = self.STD_EJ_STEP
        if self.is_in_light_barrier() == 0:
            self.set_port_mode(port=0, mode=2)
            while not self.is_in_light_barrier():
                self.move(position=steps, speed=self.STD_EJ_SPEED,
                          timeout=30, cmd_mode=2)
                steps += step_size

        # move out of de light barrier and inside again
        # this pattern is very important to ensure correct direction for
        # all commands within and related to this class
        if self.is_in_light_barrier() == 1:
            # move inside the light barrier
            # this can be a upward move when previous if clause was executed
            # or an upward or downward move depending on the excenter position
            while self.is_in_light_barrier():
                self.move_abs(position=steps, speed=self.STD_EJ_SPEED,
                              timeout=30)
                steps += step_size
            # if outside light barrier was reached we are sure to have moved
            # a sufficient amount ot steps to re-detect the light barrier
            while self.is_in_light_barrier() == 0:
                self.set_port_mode(port=0, mode=2)
                home_pos = 0  # move as far upwards as possible
                self.move(position=home_pos, speed=self.STD_EJ_SPEED,
                          timeout=30, cmd_mode=2)
                break  # no forever run if light barrier switches to False again

        self.init()  # do init again to set actual position to 0

    def gripper_out(self) -> None:
        """Gripper out by activation of magnet valve 1.

        Wait a little to complete gripper move, because set port is not able
        to wait until finished.
        """

        self.set_port(port=3, value=1000, length=2)
        time.sleep(2*PORT_ACTUALIZE_TIME)

    def gripper_in(self) -> None:
        """Gripper in by deactivation of magnet valve 1.

        Wait a little to complete gripper move, because set port is not able
        to wait until finished.
        """

        self.set_port(port=3, value=0, length=2)
        time.sleep(PORT_ACTUALIZE_TIME)

    def get_distance(self) -> int:
        """Get distance reported by sonic sensor.

        Returns:
            value of sonic sensor
        """

        return self.get_port(port=13)

    def is_gripper_out(self) -> bool:
        """Tells if magnet valve is powered (gripper out) or not.

        Returns:
            value of sensor for gripper position (in or out)
        """

        return bool(self.get_port(port=6))

    def eject(self, eject_position: int) -> None:
        """Retrieve tip to eject small pipette tips.

        Args:
             eject_position: position of pipette head depending on tip type
        """

        self.move_abs(
            position=eject_position, speed=self.STD_EJ_SPEED, timeout=10)

    def enable_take_pipette_tip(self, pick_position: int) -> None:
        """Moves tip so that small pipette tips can be picked.

        Args:
             pick_position: position of pipette head depending on tip type
        """

        self.move_abs(
            position=pick_position, speed=self.STD_EJ_SPEED, timeout=30)

    def is_in_light_barrier(self) -> bool:
        """Returns value for light barrier sensor.

        Returns:
            value of light barrier, inverted for better readability
        """

        return not bool(self.get_port(port=0))
