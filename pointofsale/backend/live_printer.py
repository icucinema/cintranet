from carrot.connection import BrokerConnection

from config import BROKER_CONFIG, PRINTER_CONFIG, LIVE_PRINTER_CLASS, LIVE_PRINTER_SETTINGS, LIVE_CASHDRAWER_CLASS, LIVE_CASHDRAWER_SETTINGS

from pointofsale import printer, hardware

if __name__ == '__main__':
    conn = BrokerConnection(**BROKER_CONFIG)

    hard_printer = getattr(hardware, LIVE_PRINTER_CLASS)(**LIVE_PRINTER_SETTINGS)
    hard_cashdrawer = getattr(hardware, LIVE_CASHDRAWER_CLASS)(printer=hard_printer, **LIVE_CASHDRAWER_SETTINGS)
    
    registry = printer.PrinterRegistry(PRINTER_CONFIG['registry'], PRINTER_CONFIG['auth_token'])
    p = printer.LivePrinter(hard_printer, hard_cashdrawer, PRINTER_CONFIG['name'], registry, conn)
    pm_handler = printer.PrinterMessageThread(p)
    
    pm_handler.start()
    while True:
        pm_handler.join(1)
        if not pm_handler.is_alive():
           break
