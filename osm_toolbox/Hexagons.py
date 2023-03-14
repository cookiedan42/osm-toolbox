import numpy as np
import shapely.geometry as sg

def build_hexagon(centre,radius):
    '''
    build a hexagon Polygon from a centre of x,y and a hexagon edge length
    hexagon edge length is equal to distance from centre to a corner
    '''
    x,y = centre
    
    Rcos = np.cos(np.pi/3)
    Rsin = np.sin(np.pi/3)
    points = [
        (x-radius, y),
        (x-radius*Rcos, y+radius*Rsin),
        (x+radius*Rcos, y+radius*Rsin),
        (x+radius, y),
        (x+radius*Rcos, y-radius*Rsin),
        (x-radius*Rcos, y-radius*Rsin),
             ]
    return sg.Polygon(points)


def build_square(centre,edgeLength):
    x,y = centre
    r = edgeLength/2
    points = [
        (x-r,y-r),
        (x-r,y+r),
        (x+r,y+r),
        (x+r,y-r),
    ]
    return sg.Polygon(points)

def build_square_grid(bounds,edgeLength):
    '''
    bounds: bounds of region to be gridded
    edgeLength : length of square edges
    return list of shapely square polygons
    '''
    minx,miny,maxx,maxy = bounds
    dx = edgeLength
    dy = edgeLength

    squares = []
    x = minx
    y = miny
    while  x <= maxx + dx/2:
        while y <= maxy + dy/2:
            squares.append(build_square((x,y),edgeLength))
            y+= dy
        y = miny
        x+=dx
    return squares


def build_hex_grid(bounds,edgeLength):
    '''
    using shape.bounds in form of minx,miny,maxx,maxy
    and radius (edge length) of hexagon grid,
    produce a hexagon grid that tiles the bounding box
    '''
    minx,miny,maxx,maxy = bounds
    radius = edgeLength

    dy = 2*radius * np.sin(np.pi/3)
    dx = 3*radius
    
    hexes = []
    
    # first set centred at minx miny
    x = minx
    y = miny
    while  x <= maxx + radius:
        while y <= maxy + dy/2:
            hexes.append(build_hexagon((x,y),radius))
            y+= dy
        y = miny
        x+=dx
        
    # second set offset by +0.5 deltas in each direction
    x = minx + 0.5*dx
    y = miny + 0.5*dy
    while  x <= maxx + radius:
        while y <= maxy + dy/2:
            hexes.append(build_hexagon((x,y),radius))
            y+= dy
        y = miny + dy/2
        x+=dx  
    # return a list of hexagon polygon features
    return hexes