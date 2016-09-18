# -----------------------------------------------------------------------------
# Copyright (c) Ben Kuster 2016, all rights reserved.
#
# Created: 	2016-09-16
# Version: 	0.1
# Purpose: 	Reads the XML Tree of a CityGML Bridge and writes a CSG representing it
#
# This software is provided under the GNU GPLv2
# WITHOUT ANY WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# If no license was provided, see <http://www.gnu.org/licenses/>
# -----------------------------------------------------------------------------
import re
import string
import random
from sympy import Point3D, Plane, N

from XmlReader import XmlReader

class ConstructionElement():
    def __init__(self, elem):
        self.elem = elem
        self.name = ''
        self.planes = []

    def parse(self, lod, ns):
        name = self.elem.find('./gml:name', ns)
        if not name.text:
            self.name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        else:
            self.name = re.sub(' ', '_', name.text)

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

    def writeExteriorCsg(self):
        solidDef = 'solid {0}{1} = '.format(self.name, '-exterior')
        for i in range(len(self.planes)):
            plane = self.planes[i]
            pointStr = '{0}'.format(self.__convertSympy(plane.p1.args))
            normStr = '{0}'.format(self.__convertSympy(plane.normal_vector))

            solidDef += 'plane({0};{1})'.format(
                re.sub('\\(|\\)', '', pointStr),
                re.sub('\\(|\\)', '', normStr)
            )

            if i == len(self.planes)-1:
                solidDef += ';\n'
            else:
                solidDef += ' and '

        return solidDef

    def __convertSympy(self, tup):
        return tuple([N(x) for x in tup])

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
        text = 'algebraic3d\n'
        exteriors = []
        for elem in self.outerConstruction:
            exteriors.append(elem.name + '-exterior')
            text += elem.writeExteriorCsg()

        text += 'solid bridge = '
        for i in range(len(exteriors)):
            text += exteriors[i]
            if i == len(exteriors)-1:
                text += ';\n'
            else:
                text += ' or '

        text += 'tlo bridge;'
        with open(fileName, 'w') as f:
            f.write(text)
