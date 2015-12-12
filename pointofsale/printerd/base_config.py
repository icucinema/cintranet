PRINTER_CONFIG = {
    'name': 'Luke Laptop',
    'registry': 'https://staff.icucinema.co.uk/pointofsale/printers/',
    'auth_token': '8c591bda0c0873f3fbf8e4c15c774c6f0fd52a05',
    'id': 3,
    'live': True,
}

LIVE_PRINTER_CLASS = 'SerialTicketPrinter'
LIVE_PRINTER_SETTINGS = {
    'template_dir': 'templates/',
#    'before_report': '1b6100',
#    'after_report': '0c',
#    'template_name': 'ibm.txt',
    'port': '/dev/ttyUSB0',
    'baudrate': 19200,
    'backend_name': 'cbm',
}

#LIVE_CASHDRAWER_CLASS = 'PrinterSerialCashDrawer'
LIVE_CASHDRAWER_CLASS = 'CashDrawer'
LIVE_CASHDRAWER_SETTINGS = {
#    'magic_string': '1b70021f0f'
}
