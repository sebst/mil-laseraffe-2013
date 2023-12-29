import logging
from typing import Dict
from typing import Optional
import threading
import mcs

log = logging.getLogger(__name__)


class Axis(mcs.HardwareDevice):

    # Overload empty child class port and parameters dicts for convenience.
    # As defined in CPC firmware document CPC_FW.docx of 2018-12-06:
    parameters = {
    }
    ports = {
    }
    
    def __init__(self, mcs_device: mcs.McsDevice,
                 parameters: Optional[Dict[str, mcs.DataPort]] = None,
                 ports: Optional[Dict[str, mcs.DataPort]] = None,
                 name: Optional[str] = None, ) -> None:
        super().__init__(mcs_device, parameters, ports, name)
        self.connected = None

    def is_connected(self):
        if self.connected is None:
            self.connected = self.is_connected()
        return self.connected

    def get_ref_sensor(self):
        return self.get_port(port=0)

    def get_qt_300(self):  # z only
        """ deprecated, use getCapacitiveSensor() """
        return self.get_port(port=2)

    def get_liquid_detect_qt_300(self):  # z only
        e = threading.Event()
        pos, speed = self.get_move()
        if speed >= 2499:
            log.debug("high speed")
            qt_300_value = float(self.get_qt_300())
            for i in range(10):
                e.wait(0.01)
                qt_300_value = qt_300_value + float(self.get_qt_300())
            qt_300_value = qt_300_value/11
        else:
            log.debug("low speed")
            qt_300_value = float(self.get_qt_300())
            for i in range(30):
                e.wait(0.0005)
                qt_300_value = qt_300_value + float(self.get_qt_300())
            qt_300_value = qt_300_value/31
        new_qt_300_value = float(self.get_qt_300())
        qt_300_diff = qt_300_value - new_qt_300_value
        qt_300_value = new_qt_300_value

        log.debug("qt_300_diff: %r" % qt_300_diff)

        if qt_300_diff <= -2.5 and pos <= 80:
            return "AIR"

        elif qt_300_diff >= 15 or qt_300_diff <= -2.5:
            return "LIQUID"
        else:
            return "AIR"

    def get_capacitive_sensor(self):  # z only
        return self.get_port(port=2)

    def get_bottom_detect(self):  # z only
        return self.get_port(port=1)

    def get_liquid_detect(self):  # z only
        return self.get_port(port=4)

    def get_liquid_detect_concrete(self):  # z only
        r = self.get_port(port=4)

        if r != 0:
            return "LIQUID"
        else:
            return "AIR"

    def reset_bottom_detect(self):  # z only
        return self.set_port(length=1, port=1, value=0)

    def get_position(self):
        pos, speed = self.get_move()
        pos= float(pos)/10
        return pos

    def activate_ref_sensor_detect(self, setting=True):
        if setting:
            mode = 2
        else:
            mode = 0
        self.set_port_mode(port=0, mode=mode)

    def activate_bottom_detect(self, setting=True):
        if setting: 
            mode = 2
        else:       
            mode = 0
        self.set_port_mode(port=1, mode=mode)

    def activate_liquid_detect(self, setting=True):
        if setting: 
            mode = 2
        else:       
            mode = 0
        self.set_port_mode(port=4, mode=mode)

    def move_to(self, cmd_mode=0, position=0, speed=0, timeout=30):
        try:
            if cmd_mode.upper() == "STOP": 
                cmd_mode = 2
        except:
            pass

        position = int(position*10)
        speed = int(speed*100)
        self.move(cmd_mode=cmd_mode, position=position, speed=speed,
                  timeout=timeout)

    def rotate_shaker(self, speed):
        if speed < 0:
            direction = 0
            speed = -speed
        else:
            direction = 1
        self.rotate(cmd_mode=0, direction=direction, speed=int(speed*100))
        
    # ======= Setting parameter functions: Just for setting parameters ========
    
    # =============================================
    def set_parameters_amp_y(self):
    # =============================================
        # canID=0x412

        self.reset(0x03)
        log.debug("aMp Y Parameters")
        # calibration for units 0,1mm ; 0,01mm/s ; 1mm/sec/sec
    
        # Y  Maxon A-max22 12V GB 110056 Planetengetriebe 19:1 0,5Nm 11xxxx
        # Encoder Digital MR 201935 (16er Encoder)
        self.set_parameter(parameter=0,  value=0x20,  length=1)   #  0x20=init without sensor 0x21=init with sensor
        self.set_parameter(parameter=1,  value=12,    length=1)   # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2,  value=1406,  length=2)   # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3,  value=10,    length=1)   # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4,  value=13731, length=2)   # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5,  value=10,    length=1)   # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6,  value=8184,  length=2)   # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7,  value=2000,  length=2)   # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=8,  value=30000, length=2)   # Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9,  value=500,   length=2)   # Beschleunigung (user-Units/(sek*sek))
        # self.set_parameter(parameter=10, value=0, length=4)   # position range min. (user-Units) set according to param 26
        self.set_parameter(parameter=11, value=1680,  length=4)   # position range max. (user-Units)
        self.set_parameter(parameter=12, value=600,   length=4)   # discrete pos #0 (user-Units)
        self.set_parameter(parameter=13, value=700,   length=4)   # discrete pos #1
        self.set_parameter(parameter=14, value=800,   length=4)   # discrete pos #2
        self.set_parameter(parameter=15, value=900,   length=4)   # discrete pos #3
        self.set_parameter(parameter=16, value=0,     length=4)   # discrete pos #4
        self.set_parameter(parameter=17, value=0,     length=4)   # discrete pos #5
        self.set_parameter(parameter=18, value=1000,  length=2)   # Wert fuer den Positionsfehler in userUnits (schnell)
        self.set_parameter(parameter=19, value=4,     length=2)   # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=200,   length=2)   # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=50,    length=2)   # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=4000,  length=2)   # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=250,   length=2)   # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=1,     length=1)   # Achsenrichtung
        self.set_parameter(parameter=25, value=200,   length=2)   # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=13,    length=4)   # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=0,     length=2)   # Korrektur nach Oben beim Aufsetzen(user-Units)# (nur sinnvoll f?r Z-Achse mit Aufsetzdetektor)
        self.set_parameter(parameter=28, value=5,     length=2)   # Wert fuer den Positionsfehler in userUnits (langsam)
        self.set_parameter(parameter=29, value=1,     length=2)   # Praezisionsbereich(in userUnits: 1 uU = 12 Motorinkremente)
        self.set_parameter(parameter=30, value=6000,  length=2)   # Nachregelungszeit(1/2 msek.)

    # =============================================
    def set_parameters_amp_z(self):
    # =============================================
        # canID=0x413

        self.reset(0x03)
        log.debug("aMp Z Parameters...")
        # calibration for units 0,1mm ; 0,01mm/s ; 1mm/sec/sec
    
        # Z  Maxon A-max16 12VDC 110056 Planetengetriebe 29:1 0,15Nm 118185
        # um 8mm verlaengerte Ausgangswelle Encoder Digital MR 201935
        # 16er Encoder
        self.set_parameter(parameter=0,  value=0x31,  length=1)  # 0x31=init with sensor 0x30=init without sensor
        self.set_parameter(parameter=1,  value=10,    length=1)  # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2,  value=547,   length=2)  # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3,  value=10,    length=1)  # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4,  value=21374, length=2)  # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5,  value=10,    length=1)  # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6,  value=12740, length=2)  # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7,  value=2000,  length=2)  # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=8,  value=30000, length=2)  # Betriebs-Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9,  value=1500,  length=2)  # Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=10, value=-3,    length=4)  # position range min.(user-Units)
        self.set_parameter(parameter=11, value=1305,  length=4)  # position range max.(user-Units) #0ld 1305
        self.set_parameter(parameter=12, value=600,   length=4)  # discrete pos #0(user-Units)
        self.set_parameter(parameter=13, value=700,   length=4)  # discrete pos #1
        self.set_parameter(parameter=14, value=800,   length=4)  # discrete pos #2
        self.set_parameter(parameter=15, value=900,   length=4)  # discrete pos #3
        self.set_parameter(parameter=16, value=0,     length=4)  # discrete pos #4
        self.set_parameter(parameter=17, value=0,     length=4)  # discrete pos #5
        self.set_parameter(parameter=18, value=1500,  length=2)  # Wert fuer den Positionsfehler in user-units
        self.set_parameter(parameter=19, value=4,     length=2)  # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=600,   length=2)  # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=20,    length=2)  # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=550,   length=2)  # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=400,   length=2)  # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=0,     length=1)  # Achsenrichtung
        self.set_parameter(parameter=25, value=200,   length=2)  # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=-3,    length=4)  # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=0,     length=2)  # Korrektur nach Oben beim Aufsetzen(user-Units)
        self.set_parameter(parameter=28, value=1,     length=2)  # Wert fuer den Positionsfehler in userUnits (langsam)
        self.set_parameter(parameter=29, value=2,     length=2)  # Praezisionsbereich(in userUnits: 1 uU = 12 Motorinkremente)
        self.set_parameter(parameter=30, value=3000,  length=2)  # Nachregelungszeit(msek.)
    
        log.debug("aMp Z Port Parameters...")
        # Port parameters for bottom detection
        # Enable for Version 3 firmware
        self.set_port_parameter(port=1, parameter=0, value=0,    length=2)  # Port-Wert-Offset
        self.set_port_parameter(port=1, parameter=1, value=0,    length=1)  # Port-Wert-CALS
        self.set_port_parameter(port=1, parameter=2, value=1,    length=2)  # Port-Wert-CALM
        self.set_port_parameter(port=1, parameter=3, value=200,  length=2)  # bottom edge: delta QT300 zwischen zwei Abfragen, das als Stop-Kriterium verwendet wird (Fahrt nach unten)
        self.set_port_parameter(port=1, parameter=4, value=0,    length=2)  # Noise edge
        self.set_port_parameter(port=1, parameter=5, value=4300, length=2)  # Error edge: QT300-Wert bei dessen Ueberschreiten ein Fehler ausgegeben wird, da die Nadel raus ist
        self.set_port_parameter(port=1, parameter=6, value=80,   length=2)  # release edge: delta QT300 zwischen zwei Abfragen, das als Stop-Kriterium verwendet wird (Fahrt nach oben)
        self.set_port_parameter(port=1, parameter=7, value=3,    length=2)  # Count of plateau points after release: Anzahl der QT300-Abfragen, bei denen das Stop-Kriterium erfuellt bleiben muss, um gueltig zu sein

    # =============================================
    def set_parameters_amp_x(self):  # miniSampler
    # =============================================
        # canID=0x491

        self.reset(0x03)
        log.debug("aMp X Parameters (miniSampler) ...")
    
        self.set_parameter(parameter=0,  value=18,    length=1)  # Konfiguration  Maxon, 32er Encoder
        self.set_parameter(parameter=1,  value=12,    length=1)  # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2,  value=1450,  length=2)  # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3,  value=10,    length=1)  # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4,  value=14165, length=2)  # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5,  value=10,    length=1)  # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6,  value=8443,  length=2)  # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7,  value=3000,  length=2)  # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=8,  value=30000, length=2)  # Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9,  value=600,   length=2)  # Beschleunigung (user-Units/(sek*sek))
        self.set_parameter(parameter=10, value=-10,   length=4)  # position range min. (user-Units)
        self.set_parameter(parameter=11, value=1280,  length=4)  # position range max. (user-Units)
        self.set_parameter(parameter=12, value=0,     length=4)  # discrete pos #0 (user-Units)
        self.set_parameter(parameter=13, value=0,     length=4)  # discrete pos #1
        self.set_parameter(parameter=14, value=0,     length=4)  # discrete pos #2
        self.set_parameter(parameter=15, value=0,     length=4)  # discrete pos #3
        self.set_parameter(parameter=16, value=0,     length=4)  # discrete pos #4
        self.set_parameter(parameter=17, value=0,     length=4)  # discrete pos #5
        self.set_parameter(parameter=18, value=1000,  length=2)  # Wert fuer den Positionsfehler in userUnits
        self.set_parameter(parameter=19, value=4,     length=2)  # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=100,   length=2)  # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=100,   length=2)  # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=300,   length=2)  # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=20000, length=2)  # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=0,     length=1)  # Achsenrichtung
        self.set_parameter(parameter=25, value=200,   length=2)  # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=0,     length=4)  # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=0,     length=2)  # not used (correction value z-axis bottom detect)
        self.set_parameter(parameter=28, value=10,    length=2)  # Schleppfehler, Wert f?r Positionsfehler in userUnits bei kleineren Geschwindigkeiten
        self.set_parameter(parameter=29, value=1,     length=2)  # Pr?zisionsbereich f?r Positionierung (Deltaumgebung erlaubte Abweichung)
        self.set_parameter(parameter=30, value=4000,  length=2)  # maximale Zeitspanne in 1/2 Millisec f?r Positionskorrekturbewegung
        self.set_parameter(parameter=31, value=75,    length=2)  #  uSek/0.5 min. 8 und max. 128 (75 = 1.5A im Stand) 87=1,75

    ##############################

    # =============================================
    def set_parameters_mq_y(self):
    # =============================================
        # canID=0x412

        self.reset(0x03)
        log.debug("MQ Y Parameters")
        # calibration for units 0,1mm ; 0,01mm/s ; 1mm/sec/sec
    
        # Y  Maxon A-max22 12V GB 110056 Planetengetriebe 19:1 0,5Nm 11xxxx
        # Encoder Digital MR 201935 (16er Encoder)
        self.set_parameter(parameter=0, value=0x20,         length=1)   #  0x20=init without sensor 0x21=init with sensor
        self.set_parameter(parameter=1, value=12,           length=1)   # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2, value=1389,         length=2)   # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3, value=10,           length=1)   # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4, value=13570,        length=2)   # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5, value=10,           length=1)   # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6, value=8088,         length=2)   # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7, value=4000,         length=2)   # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit) !! von 2000 auf 4000 for MQX-Arm
        self.set_parameter(parameter=8, value=10000,        length=2)   # Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9, value=375,          length=2)   # Beschleunigung (user-Units/(sek*sek))
        self.set_parameter(parameter=10, value=-100,        length=4)   # position range min. (user-Units) set according to param 26
        # self.set_parameter(parameter=11, value=1700,        length=4)   # position range max. (user-Units)
        self.set_parameter(parameter=12, value=600,         length=4)   # discrete pos #0 (user-Units)
        self.set_parameter(parameter=13, value=700,         length=4)   # discrete pos #1
        self.set_parameter(parameter=14, value=800,         length=4)   # discrete pos #2
        self.set_parameter(parameter=15, value=900,         length=4)   # discrete pos #3
        self.set_parameter(parameter=16, value=0,           length=4)   # discrete pos #4
        self.set_parameter(parameter=17, value=0,           length=4)   # discrete pos #5
        self.set_parameter(parameter=18, value=500,         length=2)   # Wert fuer den Positionsfehler in userUnits (schnell)
        self.set_parameter(parameter=19, value=4,           length=2)   # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=int(6000/8), length=2)   # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=0,           length=2)   # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=0,           length=2)   # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=int(4000/8), length=2)   # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=1,           length=1)   # Achsenrichtung
        self.set_parameter(parameter=25, value=200,         length=2)   # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=0,           length=4)   # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=0,           length=2)   # Korrektur nach Oben beim Aufsetzen(user-Units)# (nur sinnvoll f?r Z-Achse mit Aufsetzdetektor)
        self.set_parameter(parameter=28, value=1,           length=2)   # Wert fuer den Positionsfehler in userUnits (langsam)
        self.set_parameter(parameter=29, value=3,           length=2)   # Praezisionsbereich(in userUnits: 1 uU = 12 Motorinkremente)
        self.set_parameter(parameter=30, value=3000,        length=2)   # Nachregelungszeit(1/2 msek.)

    # =============================================
    def set_parameters_mq_z(self):
    # =============================================
        # canID=0x413

        self.reset(0x03)
        log.debug("MQ Z Parameters...")
        # calibration for units 0,1mm ; 0,01mm/s ; 1mm/sec/sec
    
        # Z  Maxon A-max16 12VDC 110056 Planetengetriebe 29:1 0,15Nm 118185
        # um 8mm verlaengerte Ausgangswelle Encoder Digital MR 201935 16er Encoder
        self.set_parameter(parameter=0,  value=0x30,        length=1)  #  0x31=init with sensor 0x30=init without sensor
        self.set_parameter(parameter=1,  value=10,          length=1)  # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2,  value=544,         length=2)  # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3,  value=10,          length=1)  # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4,  value=21257,       length=2)  # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5,  value=10,          length=1)  # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6,  value=12670,       length=2)  # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7,  value=2000,        length=2)  # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=8,  value=8000,        length=2)  # Betriebs-Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9,  value=450,         length=2)  # Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=10, value=-5,          length=4)  # position range min.(user-Units)
        self.set_parameter(parameter=11, value=1320,        length=4)  # position range max.(user-Units)
        self.set_parameter(parameter=12, value=600,         length=4)  # discrete pos #0(user-Units)
        self.set_parameter(parameter=13, value=700,         length=4)  # discrete pos #1
        self.set_parameter(parameter=14, value=800,         length=4)  # discrete pos #2
        self.set_parameter(parameter=15, value=900,         length=4)  # discrete pos #3
        self.set_parameter(parameter=16, value=0,           length=4)  # discrete pos #4
        self.set_parameter(parameter=17, value=0,           length=4)  # discrete pos #5
        self.set_parameter(parameter=18, value=1000,        length=2)  # Wert fuer den Positionsfehler in user-units
        self.set_parameter(parameter=19, value=4,           length=2)  # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=int(9600/8), length=2)  # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=int(160/8),  length=2)  # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=int(96/8),   length=2)  # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=int(3200/8), length=2)  # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=0,           length=1)  # Achsenrichtung
        self.set_parameter(parameter=25, value=200,         length=2)  # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=0,           length=4)  # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=20,          length=2)  # Korrektur nach Oben beim Aufsetzen(user-Units)
        self.set_parameter(parameter=28, value=1,           length=2)  # Wert fuer den Positionsfehler in userUnits (langsam)
        self.set_parameter(parameter=29, value=3,           length=2)  # Praezisionsbereich(in userUnits: 1 uU = 12 Motorinkremente)
        self.set_parameter(parameter=30, value=3000,        length=2)  # Nachregelungszeit(msek.)
    
    ##    log.debug("aMp Z Port Parameters...")
    ##    # Port parameters for bottom detection
    ##    # Enable for Version 3 firmware
    ##    self.set_port_parameter(port=1, parameter=0, value=0,    length=2) # Port-Wert-Offset
    ##    self.set_port_parameter(port=1, parameter=1, value=0,    length=1) # Port-Wert-CALS
    ##    self.set_port_parameter(port=1, parameter=2, value=1,    length=2) # Port-Wert-CALM
    ##    self.set_port_parameter(port=1, parameter=3, value=1000, length=2) # bottom edge: delta QT300 zwischen zwei Abfragen, das als Stop-Kriterium verwendet wird (Fahrt nach unten)
    ##    self.set_port_parameter(port=1, parameter=4, value=0,    length=2) # Noise edge
    ##    self.set_port_parameter(port=1, parameter=5, value=9999, length=2) # Error edge: QT300-Wert bei dessen Ueberschreiten ein Fehler ausgegeben wird, da die Nadel raus ist
    ##    self.set_port_parameter(port=1, parameter=6, value=80,   length=2) # release edge: delta QT300 zwischen zwei Abfragen, das als Stop-Kriterium verwendet wird (Fahrt nach oben)
    ##    self.set_port_parameter(port=1, parameter=7, value=3,    length=2) # Count of plateau points after release: Anzahl der QT300-Abfragen, bei denen das Stop-Kriterium erfuellt bleiben muss, um gueltig zu sein

    #=============================================
    def set_parameters_mq_x(self): # miniSampler
    #=============================================
        # canID=0x491

        self.reset(0x03)
        log.debug("MQ X Parameters (miniSampler) ...")
    
        self.set_parameter(parameter=0,  value=0x10,  length=1)  # Konfiguration  Maxon, 32er Encoder
        self.set_parameter(parameter=1,  value=12,    length=1)  # Kalibrierung_Beschleunigung - Shift(<<)
        self.set_parameter(parameter=2,  value=1450,  length=2)  # Kalibrierung_Beschleunigung - Multiplexer(*)
        self.set_parameter(parameter=3,  value=10,    length=1)  # Kalibrierung_Geschwindigkeit -  Shift(<<)
        self.set_parameter(parameter=4,  value=14165, length=2)  # Kalibrierung_Geschwindigkeit - Multiplexer(*)
        self.set_parameter(parameter=5,  value=10,    length=1)  # Kalibrierung_Positionierung -  Shift(<<)
        self.set_parameter(parameter=6,  value=8344,  length=2)  # Kalibrierung_Positionierung - Multiplexer(*)
        self.set_parameter(parameter=7,  value=3000,  length=2)  # Initialisierungs-Geschwindigkeit (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=8,  value=30000, length=2)  # Geschwindigkeit f?r Move_Discret() (UserUnits Geschwindigkeit)
        self.set_parameter(parameter=9,  value=600,   length=2)  # Beschleunigung (user-Units/(sek*sek))
        self.set_parameter(parameter=10, value=-20,   length=4)  # position range min. (user-Units)
        self.set_parameter(parameter=11, value=5000,  length=4)  # position range max. (user-Units)
        self.set_parameter(parameter=12, value=600,   length=4)  # discrete pos #0 (user-Units)
        self.set_parameter(parameter=13, value=700,   length=4)  # discrete pos #1
        self.set_parameter(parameter=14, value=800,   length=4)  # discrete pos #2
        self.set_parameter(parameter=15, value=900,   length=4)  # discrete pos #3
        self.set_parameter(parameter=16, value=0,     length=4)  # discrete pos #4
        self.set_parameter(parameter=17, value=0,     length=4)  # discrete pos #5
        self.set_parameter(parameter=18, value=1000,  length=2)  # Wert fuer den Positionsfehler in userUnits
        self.set_parameter(parameter=19, value=4,     length=2)  # PID_DS Regelungsfaktor
        self.set_parameter(parameter=20, value=100,   length=2)  # PID_KP Regelungsfaktor(Prop.Mitglied)
        self.set_parameter(parameter=21, value=100,   length=2)  # PID_KI Regelungsfaktor(Integr.Mitglied)
        self.set_parameter(parameter=22, value=300,   length=2)  # PID_KD Regelungsfaktor(Dif.Mitglied)
        self.set_parameter(parameter=23, value=20000, length=2)  # PID_IL Regelungsfaktor
        self.set_parameter(parameter=24, value=0,     length=1)  # Achsenrichtung
        self.set_parameter(parameter=25, value=200,   length=2)  # Init-Beschleunigung(user-Units/(sek*sek))
        self.set_parameter(parameter=26, value=0,     length=4)  # Homeposition(user-Units) am Ende von Init() angefahren und aktuelle Position auf 0 gesetzt
        self.set_parameter(parameter=27, value=0,     length=2)  # not used (correction value z-axis bottom detect)
        self.set_parameter(parameter=28, value=1,     length=2)  # Schleppfehler, Wert f?r Positionsfehler in userUnits bei kleineren Geschwindigkeiten
        self.set_parameter(parameter=29, value=3,     length=2)  # Pr?zisionsbereich f?r Positionierung (Deltaumgebung erlaubte Abweichung)
        self.set_parameter(parameter=30, value=3000,  length=2)  # maximale Zeitspanne in 1/2 Millisec f?r Positionskorrekturbewegung
        self.set_parameter(parameter=31, value=75,    length=2)  #  uSek/0.5 min. 8 und max. 128 (75 = 1.5A im Stand) 87=1,75

    # ============= Setting parameter functions: UNTIL HERE ===================

