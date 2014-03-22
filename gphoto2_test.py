#!/usr/bin/env python3


import subprocess
import time
import random


def devices():
    return Device.all()


class Device:

    @staticmethod
    def _exec(cmd):
        return subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

    @classmethod
    def all(cls):
        return [
            Device('Canon EOS 500D', 'usb:001'),
            Device('Canon EOS 500D', 'usb:002')]

    def __init__(self, camera, port):
        self.camera = camera
        self.port = port

    def capture(self, path):
        time.sleep(0.4)

        text = random.randint(100, 999)
        path = path.replace('%C', 'jpg')

        tmpl = ('convert -size 2000x2000 xc:white -pointsize 1000'
                ' -draw "text 100,1500 \'{0}\'" "{1}"')

        self._exec(tmpl.format(text, path))

    def __str__(self):
        return '{0} {1}'.format(self.camera, self.port)

    def __repr__(self):
        return 'Device("{0}", "{1}")'.format(self.camera, self.port)

    def __lt__(self, other):
        return self.port < other.port

    def __hash__(self):
        return hash((self.camera, self.port))

