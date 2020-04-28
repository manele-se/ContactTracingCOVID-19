
import time
from device import Device

d1 = Device()
d2 = Device()

print(f'd1 position: {d1.lat:1.6f}, {d1.lng:1.6f}')
print(f'd2 position: {d2.lat:1.6f}, {d2.lng:1.6f}')

if d2.lat < d1.lat:
    print('d2 south of d1')
else:
    print('d2 north of d1')

if d2.lng < d1.lng:
    print('d2 west of d1')
else:
    print('d2 east of d1')

print(f'Distance: {d1.distance_to(d2):1.1f}m')
print(f'Bearing: {d1.bearing_to(d2):1.1f}')

for i in range(0,100):
    time.sleep(1)
    d1.tick(1)
    d2.tick(1)
    print(f'\rd1 position: {d1.lat:1.6f}, {d1.lng:1.6f}, {d1.distance_to(d2):1.1f}m from d2', end='', flush=True)

print(f'Link: https://www.google.com/maps/place/@{d1.lat},{d1.lng}')