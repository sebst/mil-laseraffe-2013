# -*- coding: utf-8 -*-
import logging
import sys
import mcs

log_format = (f'%(asctime)s %(levelname)-8.8s %(name)-20.20s '
              f'%(message)s')
formatter = logging.Formatter(log_format)
console_handler = logging.StreamHandler(sys.stdout)  # instead of stderr
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
log_mcs = logging.getLogger("mcs")
log_mcs.addHandler(console_handler)
log_mcs.setLevel(logging.DEBUG)
log = logging.getLogger(__name__)


def run() -> None:
    can = mcs.get_mcs_tml()
    try:
        axis_prop = mcs.tml.AxisProperties(
            axis_id=6,
            name="Z_MC",
            unit="mm",
            transmission_ratio=0.1,
            sampling_period=0.001,
            no_encoder_lines=500,
            max_current=32000)
        z = mcs.tml.TechnosoftAxis(can.ext_msg_rcv, axis_prop)

        pos = 50
        speed = 20
        current_lim = None
        mode = 1

        #z.axis_off()
        #z.axis_on()

        z.write_c_acc(500)
        z.write_c_dec(500)
        z.write_c_spd(20)
        z.write_home_spd(2)
        z.write_home_pos(-1)
        #z.home_crt0()
        #z.home_time0()
        z.homing(17)

        z.move(pos=pos, spd=speed, crt_lim=current_lim,
               drv_mode=mode, wait_ready=10)

    finally:
        try:
            can.close()
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    run()
