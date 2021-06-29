from phgl_imp import *

class usb_device_model(module):
    def set_par(self):
        super(usb_device_model, self).set_par()
        self.p.par('MODE', 1, vinst = 1)

    def check_par(self):
        super(usb_device_model, self).check_par()
        self.pm.vuser  = [
            ('inc' , '../../common/vips/usb_device_model/usb_device_model.v')]

    def set_port(self):
        super(usb_device_model, self).set_port()
        self.no_crg()

        self.io.var(inp('Vbus'))
        self.io.var(inoutp('Dp'))
        self.io.var(inoutp('Dm'))
        self.io.var(inp('GND'))
