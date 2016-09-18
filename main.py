import argparse

from bridge.Bridge import Bridge

parser = argparse.ArgumentParser(description='Read a city GMLm, export CSG')
parser.add('--id', help='the GML ID of the bridge model to extract', required=True)
parser.add('--gml', help='the GML file name', required=True)
parser.add('--csg', help='output file name', required=True)
args = parser.parse_args()

bridge = new Bridge(args.id)
bridge.parse(args.gml)
bridge.write(args.csg)
