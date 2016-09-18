import re
from sympy import Point3D, Plane

from util.XmlReader import XmlReader

class ConstructionElement():
    def __init__(self, elem):
        self.elem = elem
        self.planes = []

    def parse(self, lod, ns):
        surfaces = self.elem.findall('./brid:lod{0}Geometry/gml:MultiSurface/gml:surfaceMember/gml:Polygon'.format(lod), ns)
        for surf in surfaces:
            exterior = surf.find('./gml:exterior/gml:LinearRing', ns)
            interior = surf.find('./gml:interior', ns)
            if interior:
                print('found poly interior, cant handle, ignoring')

            positions = exterior.findall('.//gml:pos', ns)
            pointIndexes = [0, int(len(positions)/4), 2*int(len(positions)/4)]
            points = []
            for i in pointIndexes:
                point = re.sub('\\s+', ',', positions[i].text).split(',')
                points.append(Point3D(point))

            self.planes.append(Plane(*points))
        pass

class Bridge():
    def __init__(self, id, lod):
        self.id = id
        self.lod = lod
        self.outerConstruction = []

    def parse(self, fileName):
        reader = XmlReader()
        root = reader.getById(fileName, self.id)
        outerElems = root.findall('./brid:outerBridgeConstruction/brid:BridgeConstructionElement', reader.ns)
        for elem in outerElems:
            constElem = ConstructionElement(elem)
            self.outerConstruction.append(constElem)

        for elem in self.outerConstruction:
            elem.parse(self.lod, reader.ns)

    def write(self, fileName):
        pass
