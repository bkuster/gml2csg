import xml.etree.ElementTree as ET
import re

class XmlReader():
    def __init__(self, gml):
        self.ns = {
            'brid':'http://www.opengis.net/citygml/bridge/2.0'
            'bldg':'http://www.opengis.net/citygml/building/2.0',
            'core':'http://www.opengis.net/citygml/profiles/base/2.0',
            'gml':'http://www.opengis.net/gml',
            'xlink':'http://www.w3.org/1999/xlink'
        }

    def parse(self, fileName):
        return ET.parse(fileName)

    def getById(self, fileName, id):
        root = self.parse(fileName)
        modelDef = root.find("./CityModel/cityObjectMember[@gml:id='{0}']".format(id))
        return modelDef
