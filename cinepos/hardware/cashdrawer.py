# This is vaguely what a CashDrawer should look like
class CashDrawer(object):
    def __init__(self, **kwargs):
        pass

    def open(self):
        print "Ding! Cash drawer open"

class SerialCashDrawer(CashDrawer):
    def __init__(self, serial, magic_string, **kwargs):
        super(SerialCashDrawer, self).__init__(**kwargs)
        self.serial = serial
        self.magic_string = magic_string.decode('hex')

    def open(self):
        self.serial.write(self.magic_string)

class PrinterSerialCashDrawer(SerialCashDrawer):
    def __init__(self, printer, **kwargs):
        super(PrinterSerialCashDrawer, self).__init__(serial=printer.serial, **kwargs)