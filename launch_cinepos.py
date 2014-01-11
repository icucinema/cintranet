import os.path, sys

__author__ = 'lukegb'

if __name__ == '__main__':
    this_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(this_dir, 'cintranet'))
    sys.path.append(this_dir)
    from cinepos.cinepos import CineposApplication, HardwareInterface
    view_location = os.path.join(this_dir, "cinepos", "ui", "ui.qml")
    hw_interface = HardwareInterface(os.path.join(this_dir, 'cinepos'))
    app = CineposApplication(sys.argv, hw_interface=hw_interface, view_location=view_location, full_screen=False)
    app.exec_()