# -----------------------------------------------------------------------------
# Copyright (c) Ben Kuster 2016, all rights reserved.
#
# Created: 	2016-09-16
# Version: 	0.1
# Purpose: 	Reads the XML Tree of a CityGML Bridge and writes a CSG representing it
# -----------------------------------------------------------------------------
import re
import string
import random
from sympy import Point3D, Plane, N
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth

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
        solidDef = 'solid {0}{1} = '.format(self.name, '_exterior')
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

class MultiSurface():
    def __init__(self, elem):
        self.elem = elem
        self.planes = []
        self.names = []

    def parse(self, ns):
        surfaces = self.elem.findall('./gml:surfaceMember/gml:Polygon', ns)
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
        foundClusters = self.findSolids()
        solidDef = ''
        for k, v in foundClusters.items():
            name = 'multi_surface_{0}'.format(k)
            solidDef += 'solid {0} = '.format(name)
            self.names.append(name)
            for i in range(len(v)):
                plane = v[i]
                pointStr = '{0}'.format(self.__convertSympy(plane.p1.args))
                normStr = '{0}'.format(self.__convertSympy(plane.normal_vector))

                solidDef += 'plane({0};{1})'.format(
                    re.sub('\\(|\\)', '', pointStr),
                    re.sub('\\(|\\)', '', normStr)
                )

                if i == len(v)-1:
                    solidDef += ';\n'
                else:
                    solidDef += ' and '

        return solidDef

    def findSolids(self):
        points = []
        for plane in self.planes:
            points.append(list(self.__convertSympy(plane.p1.args)))
        points = np.array(points)
        bandwidth = estimate_bandwidth(points)
        ms = MeanShift(bandwidth, bin_seeding=True)
        ms.fit(points)
        solidGroups = np.unique(ms.labels_)
        groups = {}
        for group in solidGroups:
            groups[group] = []
            for labelIndex in ms.labels_:
                if ms.labels_[labelIndex] == group:
                    groups[group].append(self.planes[labelIndex])

        return groups

    def __convertSympy(self, tup):
        return tuple([N(x) for x in tup])

class Bridge():
    def __init__(self, id, lod):
        self.id = id
        self.lod = lod
        self.outerConstruction = []
        self.mSurf = None

    def parse(self, fileName):
        reader = XmlReader()
        root = reader.getById(fileName, self.id)
        outerElems = root.findall('./brid:outerBridgeConstruction/brid:BridgeConstructionElement', reader.ns)
        # multiSurface = root.findall('./brid:lod{0}MultiSurface/gml:MultiSurface'.format(self.lod), reader.ns)
        for elem in outerElems:
            constElem = ConstructionElement(elem)
            self.outerConstruction.append(constElem)

        for elem in self.outerConstruction:
            elem.parse(self.lod, reader.ns)

        # for elem in multiSurface:
        #     self.mSurf = MultiSurface(elem)
        #     self.mSurf.parse(reader.ns)

    def write(self, fileName):
        text = 'algebraic3d\n'
        exteriors = []
        for elem in self.outerConstruction:
            exteriors.append(elem.name + '_exterior')
            text += elem.writeExteriorCsg()

        if self.mSurf:
            text += self.mSurf.writeExteriorCsg()
            for name in self.mSurf.names:
                exteriors.append(name)

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
