from CoordParsing import CoordParser, CoordParsingException
parser = CoordParser()
f = open("test_data.txt")
for line in f:
    line=line.strip().upper()
    if len(line)==0: continue
    if line[0]=="#": 
        print(line.upper())
        print("-"*80)
        continue
    print(line)
    try:
        value, message = parser.parse_coord_candidate(line)
        print("\tVALUE: "+value)
        print("\tMESSAGE: "+message)
    except CoordParsingException as e:
        print("\tREJECT: "+str(e))
    print("")