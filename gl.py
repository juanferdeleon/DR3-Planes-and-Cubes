'''
        DR1: Spheres and Materials

Creado por:

    Juan Fernando De Leon Quezada   Carne 17822

- Bitmap Class

'''

import struct
import math
import time
from random import randint as random
from random import uniform as randomDec
from obj import ObjReader
from arithmetics import *

OPAQUE = 0
REFLECTIVE = 1
TRANSPARENT = 2
MAX_RECURSION_DEPTH = 3

def char(c):
    '''1 Byte'''

    return struct.pack('=c', c.encode('ascii'))

def word(w):
    '''2 Bytes'''

    return struct.pack('=h', w)

def dword(d):
    '''4 Bytes'''

    return struct.pack('=l', d)

def color(r,g,b):
    '''Set pixel color'''

    return bytes([int(b * 255) , int(g * 255) , int(r * 255) ])

def barycentric(A, B, C, P):
    '''Convert vertices to barycentric coordinates'''
    
    cx, cy, cz = cross(V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y))

    #CZ Cannot be less 1
    if cz == 0:
        return -1, -1, -1

    #Calculate the barycentric coordinates
    u = cx/cz
    v = cy/cz
    w = 1 - (u + v)

    return  w, v, u

def reflectVector(normal, dirVector):
    reflect = 2 * dot(normal, dirVector)
    reflect = mult(reflect, normal)
    reflect = sub(reflect, dirVector)
    reflect = reflect / magnitud(reflect)
    return reflect

def refractVector(N, I, ior):
    cosi = max(-1, min(1, dot(I, N)))
    etai = 1
    etat = ior

    if cosi < 0:
        cosi = -cosi
    else:
        etai, etat = etat, etai
        N = mult(N, -1)
    
    eta = etai / etat
    k = 1 - eta * eta * (1 - (cosi * cosi))

    if k < 0:
        return None
    
    R = eta * I + (eta * cosi - k**0.5) * N
    return R / magnitud(R)

def fresnel(N, I, ior):
    cosi = max(-1, min(1, dot(I, N)))
    etai = 1
    etat = ior

    if cosi > 0:
        etai, etat = etat, etai
    
    sint = etai / etat * (max(0, 1 - cosi * cosi) ** 0.5)

    if sint >= 1:
        return 1
    
    cost = max(0, 1 - sint * sint) ** 0.5
    cosi = abs(cosi)
    Rs = ((etat * cosi) - (etai * cost)) / ((etat * cosi) + (etai * cost))
    Rp = ((etai * cosi) - (etat * cost)) / ((etai * cosi) + (etat * cost))
    return (Rs * Rs + Rp * Rp) / 2

BLACK = color(0,0,0)
WHITE = color(1,1,1)
PI = 3.14159265359

class Raytracer(object):
    '''Raytracer Class'''

    def __init__(self, width, height):
        '''Constructor'''

        self.current_color = WHITE
        self.clear_color = BLACK
        self.glCreateWindow(width, height)

        self.camPosition = V3(0, 0, 0)
        self.fov = 60

        self.scene = []

        self.pointLight = None
        self.ambientLight = None

        self.envmap = None

    def glInit(self):
        '''Initialize any internal objects that your renderer software requires'''

        pass

    def glCreateWindow(self, width, height):
        '''Initialize framebuffer, img will be this size'''

        self.height = height
        self.width = width
        self.glClear()
        self.glViewPort(0, 0, width, height)
    
    def glViewPort(self, x, y, width, height):
        '''Define the area of the image to draw on'''

        self.x = x
        self.y = y
        self.vpx = width
        self.vpy = height

    def glClear(self):
        '''Set all pixels to same color'''

        self.framebuffer = [
            [
                self.clear_color for x in range(self.width)
                ]
            for y in range(self.height)
        ]

        self.zbuffer = [
            [
                float('inf') for x in range(self.width)
                ]
            for y in range(self.height)
        ]

    def glBackground(self, texture):
        '''Background'''

        self.framebuffer = [ [ texture.getColor(x / self.width, y / self.height) for x in range(self.width)] for y in range(self.height) ]

    def glVertex(self, x, y, color = None):
        '''Change the color of a point on the screen. The x, y coordinates are 
        specific to the viewport that they defined with glViewPort().'''

        pixelX = ( x + 1) * (self.vpx  / 2 ) + self.x
        pixelY = ( y + 1) * (self.vpy / 2 ) + self.y

        if pixelX >= self.width or pixelX < 0 or pixelY >= self.height or pixelY < 0:
            return

        try:
            self.framebuffer[round(pixelY)][round(pixelX)] = color or self.current_color
        except:
            pass

    def glVertex_coord(self, x, y, color = None):
        if x < self.x or x >= self.x + self.vpx or y < self.y or y >= self.y + self.vpy:
            return

        if x >= self.width or x < 0 or y >= self.height or y < 0:
            return

        try:
            self.framebuffer[y][x] = color or self.current_color
        except:
            pass

    def glColor(self, r, g, b):
        '''Change the color glVertex() works with. The parameters must 
        be numbers in the range of 0 to 1.'''

        try:
            self.rv = round(r)
            self.gv = round(g)
            self.bv = round(b)
            self.vertex_color = color(self.rv,self.gv,self.bv)
        except ValueError:
                print('\nERROR: Please enter a number between 1 and 0\n')

    def glClearColor(self, r, g, b):
        '''Can change the color of glClear(), parameters must be numbers in the 
        range of 0 to 1.'''

        try:
            self.rc = round(r)
            self.gc = round(g)
            self.bc = round(b)
            self.clear_color = color(self.rc, self.gc, self.bc)
        except ValueError:
            print('\nERROR: Please enter a number between 1 and 0\n')

    def glFinish(self, file_name):
        '''Write Bitmap File'''
        
        bmp_file = open(file_name, 'wb')

        #File header 14 bytes
        bmp_file.write(char('B'))
        bmp_file.write(char('M'))
        bmp_file.write(dword(14 + 40 + self.width * self.height * 3))
        bmp_file.write(dword(0))
        bmp_file.write(dword(14 + 40))
        
        #File info 40 bytes
        bmp_file.write(dword(40))
        bmp_file.write(dword(self.width))
        bmp_file.write(dword(self.height))
        bmp_file.write(word(1))
        bmp_file.write(word(24))
        bmp_file.write(dword(0))
        bmp_file.write(dword(self.width * self.height * 3))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))

        # Pixeles, 3 bytes each
        for x in range(self.height):
            for y in range(self.width):
                bmp_file.write(self.framebuffer[x][y])
            
        bmp_file.close()

    def glZBuffer(self, filename):
        bmp_file = open(filename, 'wb')

        # File header 14 bytes
        bmp_file.write(bytes('B'.encode('ascii')))
        bmp_file.write(bytes('M'.encode('ascii')))
        bmp_file.write(dword(14 + 40 + self.width * self.height * 3))
        bmp_file.write(dword(0))
        bmp_file.write(dword(14 + 40))

        # Image Header 40 bytes
        bmp_file.write(dword(40))
        bmp_file.write(dword(self.width))
        bmp_file.write(dword(self.height))
        bmp_file.write(word(1))
        bmp_file.write(word(24))
        bmp_file.write(dword(0))
        bmp_file.write(dword(self.width * self.height * 3))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))
        bmp_file.write(dword(0))

        # Minimo y el maximo
        minZ = float('inf')
        maxZ = -float('inf')
        for x in range(self.height):
            for y in range(self.width):
                if self.zbuffer[x][y] != -float('inf'):
                    if self.zbuffer[x][y] < minZ:
                        minZ = self.zbuffer[x][y]

                    if self.zbuffer[x][y] > maxZ:
                        maxZ = self.zbuffer[x][y]

        for x in range(self.height):
            for y in range(self.width):
                depth = self.zbuffer[x][y]
                if depth == -float('inf'):
                    depth = minZ
                depth = (depth - minZ) / (maxZ - minZ)
                bmp_file.write(color(depth,depth,depth))

        bmp_file.close()

    def rtRender(self):
        for y in range(self.height):
            for x in range(self.width):
                # NDC
                Px = 2 * ( (x+0.5) / self.width) - 1
                Py = 2 * ( (y+0.5) / self.height) - 1

                # FOV
                t = math.tan( (self.fov * PI / 180) / 2 )
                r = t * self.width / self.height
                Px *= r
                Py *= t

                # Cam always towards -k
                direction = V3(Px, Py, -1)
                direction = div(direction, magnitud(direction))

                self.glVertex_coord(x, y, self.castRay(self.camPosition, direction))

                # material = None
                # intersect = None

                # for obj in self.scene:
                #     hit = obj.ray_intersect(self.camPosition, direction)
                #     if hit is not None:
                #         if hit.distance < self.zbuffer[y][x]:
                #             self.zbuffer[y][x] = hit.distance
                #             material = obj.material
                #             intersect = hit

                # if material is not None:
                #     self.glVertex_coord(x, y, self.pointColor(material, intersect))

    def scene_intercept(self, orig, direction, origObj = None):
        tempZbuffer = float('inf')

        material = None
        intersect = None

        for ibj in self.scene:
            if obj is not origObj:
                hit = obj.ray_intersect(orig, direction)
                if hit is not None:
                    if hit.distance < tempZbuffer:
                        tempZbuffer = hit.distance
                        material = obj.material
                        intersect = hit
        
        return material, intersect

    def castRay(self, orig, direction, origObj = None, recursion = 0):

        material, intersect = self.scene_intercept(orig, direction, origObj)

        if material is None or recursion >= MAX_RECURSION_DEPTH:
            if self.envmap:
                return self.envmap.getColor(direction)
            return self.clear_color

        objectColor = V3(material.diffuse[2] / 255, material.diffuse[1] / 255, material.diffuse[0] / 255)

        ambientColor = V3(0,0,0)
        diffuseColor = V3(0,0,0)
        specColor = V3(0,0,0)

        reflectColor = V3(0,0,0)
        refractColor = V3(0,0,0)

        finalColor = V3(0,0,0)

        shadow_intensity = 0

        # Direccion de vista
        view_dir = sub(self.camPosition, intersect.point)
        view_dir = view_dir / magnitud(view_dir)

        if self.ambientLight:
            ambientColor = V3(self.ambientLight.strength * self.ambientLight.color[2] / 255,
                                     self.ambientLight.strength * self.ambientLight.color[1] / 255,
                                     self.ambientLight.strength * self.ambientLight.color[0] / 255)

        if self.pointLight:
            # Sacamos la direccion de la luz para este punto
            light_dir = sub(self.pointLight.position, intersect.point)
            light_dir = light_dir / magnitud(light_dir)

            # Calculamos el valor del diffuse color
            intensity = self.pointLight.intensity * max(0, dot(light_dir, intersect.normal))
            diffuseColor = V3(intensity * self.pointLight.color[2] / 255,
                                     intensity * self.pointLight.color[1] / 255,
                                     intensity * self.pointLight.color[2] / 255)

            # Iluminacion especular
            reflect = reflectVector(intersect.normal, light_dir) # Reflejar el vector de luz

            # spec_intensity: lightIntensity * ( view_dir dot reflect) ** especularidad
            spec_intensity = self.pointLight.intensity * (max(0, dot(view_dir, reflect)) ** material.spec)
            specColor = V3(spec_intensity * self.pointLight.color[2] / 255,
                                  spec_intensity * self.pointLight.color[1] / 255,
                                  spec_intensity * self.pointLight.color[0] / 255)


            shadMat, shadInter = self.scene_intercept(intersect.point,  light_dir, intersect.sceneObject)
            if shadInter is not None and shadInter.distance < magnitud(sub(self.pointLight.position, intersect.point)):
                shadow_intensity = 1

        
        if material.matType == OPAQUE:
            # Formula de iluminacion, PHONG
            finalColor = (ambientColor + (1 - shadow_intensity) * (diffuseColor + specColor))
        elif material.matType == REFLECTIVE:
            reflect = reflectVector(intersect.normal, V3(direction) * -1)
            reflectColor = self.castRay(intersect.point, reflect, intersect.sceneObject, recursion + 1)
            reflectColor = V3(reflectColor[2] / 255,
                                     reflectColor[1] / 255,
                                     reflectColor[0] / 255)

            finalColor = reflectColor + (1 - shadow_intensity) * specColor

        elif material.matType == TRANSPARENT:

            outside = dot(direction, intersect.normal) < 0
            bias = 0.001 * intersect.normal
            kr = fresnel(intersect.normal, direction, material.ior)

            reflect = reflectVector(intersect.normal, V3(direction) * -1)
            reflectOrig = sum(intersect.point, bias) if outside else sub(intersect.point, bias)
            reflectColor = self.castRay(reflectOrig, reflect, None, recursion + 1)
            reflectColor = V3(reflectColor[2] / 255,
                                     reflectColor[1] / 255,
                                     reflectColor[0] / 255)

            if kr < 1:
                refract = refractVector(intersect.normal, direction, material.ior)
                refractOrig = sub(intersect.point, bias) if outside else sum(intersect.point, bias)
                refractColor = self.castRay(refractOrig, refract, None, recursion + 1)
                refractColor = V3(refractColor[2] / 255,
                                         refractColor[1] / 255,
                                         refractColor[0] / 255)


            finalColor = reflectColor * kr + refractColor * (1 - kr) + (1 - shadow_intensity) * specColor



        # Le aplicamos el color del objeto
        finalColor *= objectColor

        #Nos aseguramos que no suba el valor de color de 1
        r = min(1,finalColor[0])
        g = min(1,finalColor[1])
        b = min(1,finalColor[2])

        return color(r, g, b)


    def pointColor(self, material, intersect):

        objectColor = V3(material.diffuse[2] / 255, material.diffuse[1] / 255, material.diffuse[0] / 255)

        ambientColor = V3(0, 0, 0)
        diffuseColor = V3(0, 0, 0)
        specColor = V3(0, 0, 0)

        shadow_intensity = 0.0

        if self.ambientLight:
            ambientColor = V3(self.ambientLight.strength * self.ambientLight.color[2] / 255, self.ambientLight.strength * self.ambientLight.color[1] / 255, self.ambientLight.strength * self.ambientLight.color[0] / 255)

        if self.pointLight:
            light_dir = sub(self.pointLight.position, intersect.point)
            light_dir = div(light_dir, magnitud(light_dir))

            intensity = self.pointLight.intensity * max(0, dot(light_dir, intersect.normal))
            diffuseColor = V3(intensity * self.pointLight.color[2] / 255, intensity * self.pointLight.color[1] / 255, intensity * self.pointLight.color[2] / 255)

            view_dir = sub(self.camPosition, intersect.point)
            view_dir = div(view_dir, magnitud(view_dir))

            reflect = 2 * dot(intersect.normal, light_dir)
            reflect = mul(intersect.normal, reflect)
            reflect = sub(reflect, light_dir)

            spec_intensity = self.pointLight.intensity * (max(0, dot(view_dir, reflect)) ** material.spec)

            specColor = V3(spec_intensity * self.pointLight.color[2] / 255, spec_intensity * self.pointLight.color[1] / 255, spec_intensity * self.pointLight.color[0] / 255)

            for obj in self.scene:
                if obj is not intersect.sceneObject:
                    hit = obj.ray_intersect(intersect.point, light_dir)
                    if hit is not None and intersect.distance < magnitud(sub(self.pointLight.position, intersect.point)):
                        shadow_intensity = 1.0
        
        difPspec = sum(diffuseColor, specColor)
        shaInt = (1 - shadow_intensity)
        shaIntTDifPSpec = mul(difPspec, shaInt)
        ambPShaIntTDifPSpec = sum(ambientColor, shaIntTDifPSpec)
        finalColor = multVect(ambPShaIntTDifPSpec, objectColor)
        # finalColor = (ambientColor + (1 - shadow_intensity) * (diffuseColor + specColor)) * objectColor
        # finalColor = mul(sum(ambientColor, mul(sum(diffuseColor, specColor ), ( 1- shadow_intensity ))), objectColor)

        r = min(1, finalColor[0])
        g = min(1, finalColor[1])
        b = min(1, finalColor[2])

        return color(r, g, b)
