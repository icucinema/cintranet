import sys
import os.path

from .conf import settings
from .qtapp import CineposApplication
from .hardware import printer, cashdrawer

class HardwareInterface(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

        printer_class = getattr(settings, "PRINTER_CLASS", "TicketPrinter")
        printer_settings = getattr(settings, "PRINTER_SETTINGS", {})
        template_dir = getattr(settings, "TEMPLATE_DIR", "templates")
        if not template_dir.startswith('/'):
            template_dir = os.path.join(self.root_dir, template_dir)

        print "[printer] Using", printer_class, "with", printer_settings
        self.printer = getattr(printer, printer_class)(template_dir=template_dir, **printer_settings)

        cashdrawer_class = getattr(settings, "CASHDRAWER_CLASS", "CashDrawer")
        cashdrawer_settings = getattr(settings, "CASHDRAWER_SETTINGS", {})

        print "[cashdrawer] Using", cashdrawer_class, "with", cashdrawer_settings
        self.cashdrawer = getattr(cashdrawer, cashdrawer_class)(
            printer=self.printer, **cashdrawer_settings
        )

__author__ = 'lukegb'