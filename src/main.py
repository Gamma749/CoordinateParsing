from CoordParsing import CoordParser, CoordParsingException
import json
import sys


#Create our parsing object
parser = CoordParser()

def parse_input(line, verbose):
    """
    Parse a line of data, returning standard form string if it's valid or printing an error if it's not

    Parameters
    ----------------------------------------------------------------
    line : String
        The candidate line of data to parse

    verbose : Boolean
        Print extra information like messages from parsing

    Returns
    ----------------------------------------------------------------
    String
        Standard Form string if line was valid and could be parsed, or empty string if it couldn't be
    """
    try:
        if(verbose): print("Parsing: "+line)
        value, message = parser.parse_coord_candidate(line)
    except CoordParsingException as e:
        print("Unable to process: "+line)
        if(verbose): print("\tReason: "+ str(e))
        return ""
    #Now we have a valid value, and message on how we got that value
    if(verbose): 
        print(value)
        print(message)
    return value

def convert_standard_form_to_geoJSON(standard_form, name):
    """
    Convert a standard form string to a GeoJSON feature

    Parameters
    ----------------------------------------------------------------
    standard_form : string
        The standard form string representation of a coordinate pair

    name : string
        The name for this point

    Returns
    ----------------------------------------------------------------
    JSON object
        The geoJSON feature object representation of the standard_form coordinate pair
    """
    coordinates = standard_form.split(", ")
    geoJSON =  {
       "type":  "Feature",
       "geometry": {
           "type": "Point",
           "coordinates": [float(coordinates[1]), float(coordinates[0])]
       },
       "properties":{
           "name": name
       }
    }
    return geoJSON

def collect_geoJSON_features(features):
    """
    Collect an array of geoJSON features into a geoJSON featurecollection

    Parameters
    ----------------------------------------------------------------
    features : geoJSON feature list
        A list of geoJSON features to add to the feature collection

    Returns
    ----------------------------------------------------------------
    geoJSON feature collection
    """
    j = {
        "type": "FeatureCollection",
        "features": features
    }
    return j

if __name__ == "__main__":
    #Process any command line inputs first
    filepath = None
    verbose = False
    geoJSON_features = []
    point_number = 1
    if "-v" in sys.argv:
        #Verbose mode
        verbose = True
    if "-f" in sys.argv:
        #Use a file as input
        try:
            filepath = sys.argv[sys.argv.index("-f")+1]   
        except IndexError:
            print("Please specify a file path after -f")
            exit(1)

    #Check if we are doing things the file way
    if(filepath):
        try:
            f = open(filepath, "r")
        except FileNotFoundError:
            print("File specified does not exit")
            exit(1)
        #Read the entire line and give it to the parser
        for line in f:
            #No need to process empty lines
            if len(line)==0: continue
            value = parse_input(line, verbose)
            if len(value)==0: continue
            #Put it in the list to be consolidated later
            geoJSON_features.append(convert_standard_form_to_geoJSON(value, "Point "+str(point_number)))
            point_number+=1
        #Once done with inputs, close the file
        f.close()
    else:
        #We're not dealing with file input
        print("Please enter a coordinate pair, one per line")
        line = ""
        while True:
            try:
                line = str(input()).strip()
                if line=="EXIT": break
                if len(line)==0: continue
                value = parse_input(line, verbose)
                if len(value)==0: continue
                print("PARSED: "+value)
                geoJSON_features.append(convert_standard_form_to_geoJSON(value, "Point "+str(point_number)))
                point_number+=1
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    #That's all the input, let's convert to a geoJSON feature collection
    featureCollection = collect_geoJSON_features(geoJSON_features)

    #Get user input, parse to standard form, convert to geojson, store in list then convert all in list to geojson featurecollection, then write to disk
    data_file = open("data_file.geojson", "w")
    data_file.write(json.dumps(featureCollection, indent=4))
    data_file.close()