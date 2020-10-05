'''
        DR1 Spheres and Materials

Creado por:

    Juan Fernando De Leon Quezada   Carne 17822

Raytracer Engine 

'''
from gl import *
from texture import Texture
from obj import ObjReader
from sphere import Sphere, Material, PointLight, AmbientLight

if __name__ == '__main__':
    '''Main Program'''

    snow = Material(diffuse = color(0.87, 0.87, 0.87), spec = 32)
    buttons = Material(diffuse = color(0.43, 0.43, 0.43 ), spec = 64)
    smile = Material(diffuse = color(0, 0, 0), spec = 32)
    carrot = Material(diffuse = color(1, 0.36, 0.22), spec = 16)
    eye = Material(diffuse = color(0.6, 0.6, 0.6), spec = 128)


    width = 1080
    height = 720
    r = Raytracer(width,height)

    r.pointLight = PointLight(position = V3(-2,2,0), intensity = 1)
    r.ambientLight = AmbientLight(strength = 0.1)

    # BODY
    r.scene.append( Sphere(V3(0, 0.80, -5), 0.60, snow) ) #HEAD
    r.scene.append( Sphere(V3(0, 0,  -5), 0.75, snow) ) # BELLY
    r.scene.append( Sphere(V3(0, -1, -5), 1, snow) ) # LEGS

    # Buttons
    r.scene.append( Sphere(V3(0, 0, -2), 0.05, buttons) )
    r.scene.append( Sphere(V3(0, -0.25, -2), 0.05, buttons) )
    r.scene.append( Sphere(V3(0, -0.5, -2), 0.05, buttons) )

    # Smile
    r.scene.append( Sphere(V3(0.045, 0.25, -2), 0.02, smile) )
    r.scene.append( Sphere(V3(0.1, 0.30, -2), 0.02, smile) )
    r.scene.append( Sphere(V3(-0.045, 0.25, -2), 0.02, smile) )
    r.scene.append( Sphere(V3(-0.1, 0.30, -2), 0.02, smile) )

    # Nose
    r.scene.append( Sphere(V3(0, 0.32, -2), 0.02, carrot) )

    # Eyes
    r.scene.append( Sphere(V3(0.075, 0.4, -2), 0.04, eye) )
    r.scene.append( Sphere(V3(-0.075, 0.4, -2), 0.04, eye) )


    
    r.rtRender()

    r.glFinish('output.bmp')