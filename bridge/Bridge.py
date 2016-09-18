from ../util.XmlReader import XmlReader
class Bridge():
    def __init__(self, id):
        self.id = id

    def parse(self, fileName):
        reader = new XmlReader()
        self.xmlRoot = reader.getById(fileName, self.id)

    def write(self, fileName):
        pass
