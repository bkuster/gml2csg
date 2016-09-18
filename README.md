# GML2CSG
This small program was used for a small university project in need of meshing _CityGML_ models using _NetGen_. This requires a parsing of _GML_ to _Consolidated Solid Geometry_. This program solely outlines how this could be done, completely ignoring interiors or _BridgeInstallations_. To run the program, simply open a console of your choosing in the directory and run:
``` bash
python3 main.py --id gmlIdOfBridge --gml inFile --csg outFile
```
