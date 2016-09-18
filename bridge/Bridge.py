from util.XmlReader import XmlReader
class Bridge():
    def __init__(self, id):
        self.id = id
        self.reader = XmlReader()

    def parse(self, fileName):
        self.xmlRoot = self.reader.getById(fileName, self.id)

    def write(self, fileName):
        print(self.xmlRoot.attrib.items())
        pass
