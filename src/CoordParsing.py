# coding=utf-8
import re
from math import copysign

class CoordParsingException(Exception):
    """
    Error to be raised when Coordinate cannot be parsed successfully
    
    Parameters
    ----------------------------------------------------------------
    Message : String
        Error message to print to user to justify exception
    """
    def init(self, message):
        self.message = message
        super().__init__(self.message)


class CoordParser():
    """
    Object that can parse coordinates to standard form
    May one day add support for selecting output form
    """

    regex_dict = {}
    regex_dict_keys = []
    separators = [",", "", ";"]

    def __init__(self):
        #Let's define the regular expression matches we will use
        #We will build our regular expression by piecing together each with a separator
        #So for example, we would match standard form candidates by using
        #re.compile(standard_form + separator + standard_form+"$")
        #While this will match something like "100, 100" it will be easy to validate the numbers later
        #We're just after a clean concise solution to parsing first
        #Also, by looping through separators we can match much more

        #standard_formNoDecimal : Matches numbers -199 to 199 with no decimal
        standard_form_catch_all = "[-+]?\d+\.?\d*"

        #standard_form_nswe : Matches like 90N 90W, or 90E 90S
        #We will deal with inconsistent inputs later
        #Such as 90 N 90 S
        standard_form_nswe = "[-+]?[0-9]+(\.[0-9]+)?( *)[NSWE]"

        #degree_minute_second : Matches like 90 10 10
        degree_minute_second = "[-+]?[0-9]+ ?[°D ] *[1-6]?[0-9] ?[′'M ] *[1-6]?[0-9](\.\d*)? ?[″S\"]? *[NSWE]?"

        #degree_decimal_minute : Matches like 90 10.10
        degree_decimal_minute = "[-+]?[0-9]+ ?[°D ]?\+? *[1-6]?[0-9](\.[0-9]+)? ?[′'M]? *[NSWE]?"

        self.regex_dict_keys = ["Standard Form Catch All", "Standard Form NSWE", "Degree Minute Second", "Degree Decimal Minute"]

        self.regex_dict[self.regex_dict_keys[0]] = standard_form_catch_all
        self.regex_dict[self.regex_dict_keys[1]] = standard_form_nswe
        self.regex_dict[self.regex_dict_keys[2]] = degree_minute_second
        self.regex_dict[self.regex_dict_keys[3]] = degree_decimal_minute

    def parse_coord_candidate(self, candidate):
        """
        Takes a candidate string and tries to parse it into standard form 
        
        Parameters
        ----------------------------------------------------------------
        candidate : String
            The string to parse to a standard form coordinate

        Returns
        ----------------------------------------------------------------
        ParsedCoordinate, Message : String, String
            A standard form coordinate translation of the given candidate
            as well as any message about what needed to be done to parse the candidate

        Raises
        ----------------------------------------------------------------
        CoordParsingException
            If the candidate is not able to be parsed into a valid coordinate
        """
        candidate = candidate.upper().strip()
        #loop through all our possible patterns
        for pattern_name in self.regex_dict_keys:
            pattern_string = self.regex_dict[pattern_name]
            #And try every separator for each pattern
            for separator in self.separators:
                #Try and match the string to our candidate
                curr_pattern = re.compile("^"+pattern_string+" *"+separator+" *"+pattern_string+"$")
                #re.match returns None if no match, so this if serves to find when a match occurs
                if (re.match(curr_pattern, candidate)):
                    if(pattern_name == self.regex_dict_keys[0]):
                        return self.__parse_standard_form_catch_all(candidate, separator)
                    if(pattern_name == self.regex_dict_keys[1]):
                        return self.__parse_standard_form_nswe(candidate, separator)
                    if(pattern_name == self.regex_dict_keys[2]):
                        return self.__parse_degree_minute_second(candidate, separator)
                    if(pattern_name == self.regex_dict_keys[3]):
                        return self.__parse_degree_decimal_minute(candidate, separator)
        #Well, we didn't match anything
        raise CoordParsingException("No matches found")

    def __parse_standard_form_catch_all(self, candidate, separator, message=""):
        """
        Parse a candidate that fits the form of standard_form_catch_all

        Parameters
        ----------------------------------------------------------------
        candidate : String 
            A candidate string that fits the catch all regex

        separator : String
            The separator between the lat and long for this candidate
        
        message = "": String
            Any messages from previous parsing functions that need to be passed on
            Default the empty string

        Returns
        ----------------------------------------------------------------
            A standard form version of the candidate with correct format and separator

        Raises
        ----------------------------------------------------------------
        CoordParsingException
            If the candidate is not able to be parsed into a valid coordinate
        """
        match = re.match(re.compile(self.regex_dict["Standard Form Catch All"]+" *"+separator), candidate)
        lat = float(candidate[match.start():match.end()-len(separator)].strip())
        lng = float(candidate[match.end():].strip())
        #Ensure lat and lng are within range required
        if abs(lat)>90:
            #Latitude could be swapped with longitude
            if abs(lng)>90:
                #Latitude cannot be swapped with longitude
                raise CoordParsingException("Latitude out of range")
            temp = lat
            lat = lng
            lng = temp
            message += "Swapped latitude and longitude\n"
        if abs(lng)>180:
            #We can shift latitude by a multiple of 360 to get in range of [-180, 180]
            while(lng < -180):
                lng += 360
            while(lng > 180):
                lng -= 360
            message += "Shifted longitude to within range\n"
        
        #Okay the numbers are probably fine now

        return "{:.6f}, {:.6f}".format(lat, lng), message

    def __parse_standard_form_nswe(self, candidate, separator, message=""):
        """
        Parse a candidate that fits the form of standard_form_nswe

        Parameters
        ----------------------------------------------------------------
        candidate : String 
            A candidate string that fits the nswe regex form

        separator : String
            The separator between the lat and long for this candidate
        
        message = "": String
            Any messages from previous parsing functions that need to be passed on
            Default the empty string

        Returns
        ----------------------------------------------------------------
            A standard form version of the candidate with correct format and separator

        Raises
        ----------------------------------------------------------------
        CoordParsingException
            If the candidate is not able to be parsed into a valid coordinate
        """
        #Cast into form of lat, long then give to self.__parse_standard_form_catch_all()
        match = re.match(re.compile(self.regex_dict["Standard Form NSWE"]+" *"+separator), candidate)
        str1 = candidate[match.start():match.end()-len(separator)].strip()
        str2 = candidate[match.end():].strip()

        #Try to find if both given coordinates are the same type, which is invalid
        if(any(c in set("NS") for c in str1) and any(c in set("NS") for c in str2) 
        or any(c in set("WE") for c in str1)  and any(c in set("WE") for c in str2)):
            raise CoordParsingException("Given coordinates are not in unique directions")

        #Get the latitude and longitude the right way around
        if(str1[-1] == "N" or str1[-1] == "S" or not (str2[-1] == "N" or str2[-1] == "S")):
            lat, lat_direction = float(str1[:-1].strip()), str1[-1]
            lng, lng_direction = float(str2[:-1].strip()), str2[-1]
        else:
            lat, lat_direction = float(str2[:-1].strip()), str2[-1]
            lng, lng_direction = float(str1[:-1].strip()), str1[-1]
            message+="Swapped latitude, longitude based on order of N/S and W/E\n"

        #Do a check for limits on latitude, as user can't have made a mistake now
        if(abs(lat)>90):
            raise CoordParsingException("Latitude is out of range")

        #Check if we need to alter the sign of anything
        if(lat_direction == "S"):
            lat*=-1
        if(lng_direction == "W"):
            lng*=-1

        return self.__parse_standard_form_catch_all(str(lat)+", "+str(lng), ", ", message)
        
    def __parse_degree_minute_second(self, candidate, separator, message=""):
        """
        Parse a candidate that fits the form of degree_minute_second

        Parameters
        ----------------------------------------------------------------
        candidate : String 
            A candidate string that fits the dms regex form

        separator : String
            The separator between the lat and long for this candidate
        
        message = "": String
            Any messages from previous parsing functions that need to be passed on
            Default the empty string

        Returns
        ----------------------------------------------------------------
            A standard form version of the candidate with correct format and separator

        Raises
        ----------------------------------------------------------------
        CoordParsingException
            If the candidate is not able to be parsed into a valid coordinate
        """
        #Let's turn this into something matching standard_form_nswe
        match = re.match(re.compile(self.regex_dict["Degree Minute Second"]+" *"+separator), candidate)
        str1 = candidate[match.start():match.end()-len(separator)].strip()
        str2 = candidate[match.end():].strip()
        
        #If there exists a NSWE indicator for either of these, strip it off and store it, or set one if none exist
        if(str1[-1] in "NSWE"):
            str1_direction = str1[-1]
            str1= str1[:-1].strip()
        else:
            str1_direction="N"
            message+="No direction on first coordinate, assuming N\n"

        if(str2[-1] in "NSWE"):
            str2_direction = str2[-1]
            str2= str2[:-1].strip()
        else:
            str2_direction = "E"
            message+="No direction on second coordinate, assuming E\n"

        #Replace any special characters with spaces so we can easily split on it
        to_replace = ["°", "′", "'", "″", "\"", "+", "D", "M", "S"]
        for c in to_replace:
            str1 = str1.replace(c, " ")
            str2 = str2.replace(c, " ")

        #Should now only have numbers and spaces, so we can convert them all to floats and store as a list
        vals1 = list(map(float, str1.split()))
        vals2 = list(map(float, str2.split()))

        #And now we can do a conversion to straight degrees
        val1 = vals1[0] + copysign(vals1[1]/60, vals1[0]) + copysign(vals1[2]/3600, vals1[0])
        val2 = vals2[0] + copysign(vals2[1]/60, vals2[0]) + copysign(vals2[2]/3600, vals2[0])

        #So now we have degrees and directions, let's run it through standard_form_nswe
        return self.__parse_standard_form_nswe(str(val1)+str1_direction+", "+str(val2)+str2_direction, ", ", message)

    def __parse_degree_decimal_minute(self, candidate, separator, message=""):
        """
        Parse a candidate that fits the form of degree_decimal_minute

        Parameters
        ----------------------------------------------------------------
        candidate : String 
            A candidate string that fits the dms regex form

        separator : String
            The separator between the lat and long for this candidate
        
        message = "": String
            Any messages from previous parsing functions that need to be passed on
            Default the empty string

        Returns
        ----------------------------------------------------------------
            A standard form version of the candidate with correct format and separator

        Raises
        ----------------------------------------------------------------
        CoordParsingException
            If the candidate is not able to be parsed into a valid coordinate
        """
        #Let's turn this into something matching standard_form_nswe
        match = re.match(re.compile(self.regex_dict["Degree Decimal Minute"]+" *"+separator), candidate)
        str1 = candidate[match.start():match.end()-len(separator)].strip()
        str2 = candidate[match.end():].strip()

        #If there exists a NSWE indicator for either of these, strip it off and store it, or set one if none exist
        if(str1[-1] in "NSWE"):
            str1_direction = str1[-1]
            str1= str1[:-1].strip()
        else:
            str1_direction="N"
            message+="No direction on first coordinate, assuming N\n"

        if(str2[-1] in "NSWE"):
            str2_direction = str2[-1]
            str2= str2[:-1].strip()
        else:
            str2_direction = "E"
            message+="No direction on second coordinate, assuming E\n"

        #Replace any special characters with spaces so we can easily split on it
        to_replace = ["°", "′", "'", "″", "\"", "+", "D", "M", "S"]
        for c in to_replace:
            str1 = str1.replace(c, " ")
            str2 = str2.replace(c, " ")

        #Should now only have numbers and spaces, so we can convert them all to floats and store as a list
        vals1 = list(map(float, str1.split()))
        vals2 = list(map(float, str2.split()))

        #Combine these bad boys together and use self.__parse_standard_form_nswe to get a standard form
        val1 = vals1[0] + copysign(vals1[1]/60, vals1[0])
        val2 = vals2[0] + copysign(vals2[1]/60, vals2[0])

        return self.__parse_standard_form_nswe(str(val1)+str1_direction+", "+str(val2)+str2_direction, ", ", message)