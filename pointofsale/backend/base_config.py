BROKER_CONFIG = {
    'hostname': 'localhost',
    'port': 5672,
    'userid': 'cintranet',
    'password': 'cintranet',
    'virtual_host': '/cintranet',
}

PRINTER_CONFIG = {
    'name': 'test_printer',
    'registry': 'http://localhost:8000/pointofsale/printers/',
    'auth_token': '8c591bda0c0873f3fbf8e4c15c774c6f0fd52a05',
    'id': 1,
    'live': False,
}

#LIVE_PRINTER_CLASS = 'SerialTicketPrinter'
LIVE_PRINTER_CLASS = 'TicketPrinter'
LIVE_PRINTER_SETTINGS = {
    'template_name': 'basic.txt',
    'template_dir': 'templates/',
#    'before_report': '1b6100',
#    'after_report': '0c',
#    'template_name': 'ibm.txt',
#    'port': '/dev/ttyS0',
#    'baudrate': 19200
}

#LIVE_CASHDRAWER_CLASS = 'PrinterSerialCashDrawer'
LIVE_CASHDRAWER_CLASS = 'CashDrawer'
LIVE_CASHDRAWER_SETTINGS = {
#    'magic_string': '1b70021f0f'
}
