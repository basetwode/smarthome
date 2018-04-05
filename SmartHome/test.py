import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Application.settings")
import mmap
import django
import struct


django.setup()
from IPCDriver.models import LED

fd = os.open('/tmp/led1', os.O_RDONLY)
buf = mmap.mmap(fd, mmap.PAGESIZE, None, 1)
#    thread_check_sensors.start()
buf.seek(0)
fields = LED.get_fields(buf)

print(fields)
fd2 = os.open('/tmp/led2', os.O_RDONLY)
buf2 = mmap.mmap(fd2, mmap.PAGESIZE, None, 1)
#    thread_check_sensors.start()
buf2.seek(0)
fields2 = LED.get_fields(buf2)

print(fields2)
