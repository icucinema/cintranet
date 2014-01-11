__author__ = 'lukegb'

#PRINTER_CLASS = 'SerialTicketPrinter'
PRINTER_SETTINGS = {
    'port': '/dev/ttyUSB0',
    'template': 'ibm',
    'before_report': '1b6100',
    'after_report': '0c',
    'baudrate': 19200
}

#CASHDRAWER_CLASS = 'PrinterSerialCashDrawer'
CASHDRAWER_SETTINGS = {
    'magicstring': '1b70021f0f'
}