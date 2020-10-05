'''
        DR3

Creado por:

    Juan Fernando De Leon Quezada   Carne 17822

- Env Map Class

'''

from math import acos, atan2

PI = 3.14159265359

class Envmap(object):

    def __init__(self, path):
        self.path = path
        self.read()
    
    def read(self):
        image = open(self.path, 'rb')
        image.seek(10)
        headerSize = struct.unpack('=l', image.read(4))[0]

        image.seek(14 + 4)
        self.width = struct.unpack('=l', image.read(4))[0]
        self.height = struct.unpack('=l', image.read(4))[0]
        image.seek(headerSize)

        self.pixels = []

        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1)) / 255
                g = ord(image.read(1)) / 255
                r = ord(image.read(1)) / 255
                self.pixels[y].append(color(r,g,b))

        image.close()

    def getColor(self, direction):
        
        direction = direction / magnitud(direction)

        x = int( (atan2( direction[2], direction[0]) / (2 * PI) + 0.5) * self.width)
        y = int( acos(-direction[1]) / PI * self.height )

        return self.pixels[y][x]
