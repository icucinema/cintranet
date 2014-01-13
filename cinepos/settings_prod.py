__author__ = 'lukegb'

PRINTER_CLASS = 'SerialTicketPrinter'
PRINTER_SETTINGS = {
    'port': '/dev/ttyS0',
    'template_name': 'ibm.txt',
    'before_report': '1b6100',
    'after_report': '0c',
    'baudrate': 19200
}

CASHDRAWER_CLASS = 'PrinterSerialCashDrawer'
CASHDRAWER_SETTINGS = {
    'magic_string': '1b70021f0f'
}
