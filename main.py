# -----------------------------------------------------------------------------
# Copyright (c) Ben Kuster 2016, all rights reserved.
#
# Created: 	2016-09-16
# Version: 	0.1
# Purpose:  Entrypoint
# -----------------------------------------------------------------------------

import argparse

from Bridge import Bridge

parser = argparse.ArgumentParser(description='Read a city GMLm, export CSG')
parser.add_argument('--id', help='the GML ID of the bridge model to extract', required=True)
parser.add_argument('--gml', help='the GML file name', required=True)
parser.add_argument('--csg', help='output file name', required=True)
args = parser.parse_args()

bridge = Bridge(args.id, '3')
bridge.parse(args.gml)
bridge.write(args.csg)
