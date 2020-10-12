'''
        DR1 Spheres and Materials

Creado por:

    Juan Fernando De Leon Quezada   Carne 17822

Raytracer Engine 

'''
from gl import *
from texture import Texture
from obj import ObjReader
from envmap import Envmap
from sphere import *

if __name__ == '__main__':
    '''Main Program'''

    brick = Material(diffuse = color(0.8, 0.25, 0.25 ), spec = 16)
    stone = Material(diffuse = color(0.4, 0.4, 0.4 ), spec = 32)
    mirror = Material(spec = 64, matType = REFLECTIVE)

    glass = Material(spec = 64, ior = 1.5, matType= TRANSPARENT) 

    width = 520
    height = 520

    r = Raytracer(width,height)
    r.glClearColor(0.2, 0.6, 0.8)
    r.glClear()

    r.envmap = Envmap('envmap.bmp')

    r.pointLight = PointLight(position = V3(0,0,0), intensity = 1)
    r.ambientLight = AmbientLight(strength = 0.1)

    r.scene.append( AABB(V3(0, 1.5, -5), 1.5, stone ) )
    r.scene.append( AABB(V3(1.5, -1.5, -5), 1.5, mirror ) )
    r.scene.append( AABB(V3(-1.5, -1.5, -5), 1.5, glass ) )
    
    r.rtRender()

    r.glFinish('output.bmp')