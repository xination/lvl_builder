import sys
#
# to parse the input file
#
def readin_data( inFile ):
    '''
    read in data.txt, and pasre the data into
    list_lvl and list_gam.
    '''    
    readIn = open( inFile ,'r')     
    
    lines = readIn.readlines()
    
    # --- ignore the commented line which starts with '#'
    newlines = []
    for line in lines:
        line = line.rstrip()
        if( len(line) == 0 ): continue 
        line = line.lstrip(' ')
        if line[0] != '#':
            newlines.append(line) 
    lines = newlines
    
    if( len(lines) == 0 ):
        print( " Error: the input file %s has no data." %inFile )
        sys.exit(0)

     
    del newlines
    
    list_lvl = []
    list_gam = []
    
     
    for line in lines:
        lvl = {}
        gam = {}
        isLvl = False
        isGam = False
        elements = line.split('@')
        
        #
        # pre-check a line to make sure @key value pair
        # we counts numbers of key and value to see whether they are the same.
        checkItems = line.split() 
        num_key = 0
        num_value = 0
        for item in checkItems:
            if( item[0] == '@'): num_key += 1
            else: num_value += 1
        if( num_key != num_value):
            print(" Error: key-value pair: \n", line.rstrip() )
            print("", "^" * len(line) )
            sys.exit(0)


        #
        # pre-check a line to identify lvl or gam.
        #
        for element in elements[1:]:        
            mykey = element.split()[0]
            myvalue = element.split()[1]   
            
            # to identify whether a level or a gamma for the current line.             
            if (mykey == 'lvlE' or mykey == 'bandN' ):
               isLvl = True
               isGam = False
            if (mykey == 'Ei' or mykey == 'Ef' ):
               isLvl = False
               isGam = True

        if( isLvl ):
            has_lvlE = False
            has_bandN = False
            for element in elements[1:]:        
                mykey = element.split()[0]
                myvalue = element.split()[1]
                lvl[mykey] = myvalue

                if( mykey == 'lvlE'):  has_lvlE  = True
                if( mykey == 'bandN'): has_bandN = True
                 
            
            # validate input
            if( not has_bandN): 
                print( " Error no bandN key")
                print( line.rstrip() ); print("", "^" * len(line) )
                sys.exit( 0 )
            if( not has_lvlE ):
                print( " Error no lvlE key")
                print( line.rstrip() ); print("", "^" * len(line) )
                sys.exit( 0 )

            list_lvl.append( lvl )
            
        if( isGam ):
            has_Ei = False
            has_Ef = False
            for element in elements[1:]:        
                mykey = element.split()[0]
                myvalue = element.split()[1]
                gam[mykey] = myvalue
                if( mykey == 'Ei'): has_Ei = True
                if( mykey == 'Ef'): has_Ef = True

            # validate input
            if( not has_Ei ): 
                print( " Error no Ei key")
                print( line.rstrip() ); print("", "^" * len(line) )
                sys.exit( 0 )
            if( not has_Ef ):
                print( " Error no Ef key")
                print( line.rstrip() ); print("", "^" * len(line) )
                sys.exit( 0 )

            list_gam.append( gam )   

    # 
    # check gam's Ei and Ef are resigtered in lvl_list
    # working on it
    for gam in list_gam:
        gamEi_found = False
        gamEi =  gam['Ei']  # key 'Ei' map to str type value.
        for lvl in list_lvl:
            lvlE = lvl['lvlE'] # key 'lvlE' map to str type value.
            if( gamEi == lvlE ): gamEi_found = True
        if( not gamEi_found ): 
            print( " Gamma Error: Ei =  %s is not registered yet" %gamEi )
            sys.exit(0) 

        gamEf_found = False
        gamEf = gam['Ef']  # key 'Ei' map to str type value.
        for lvl in list_lvl:
            lvlE = lvl['lvlE'] # key 'lvlE' map to str type value.
            if( gamEf == lvlE ): gamEf_found = True
        if( not gamEf_found ): 
            print( " Gamma Error: Ef =  %s is not registered yet" %gamEf )
            sys.exit(0) 
    return list_lvl, list_gam
    pass



#
#  counting the columns ( band ) 
#
def check_total_bands( list_lvl ):
    lvl_band = []
    lvl_eng = []
    
    # analyze the number of the levels
    for i in range( len( list_lvl ) ):
        #
        # we can have @bandN 2 
        #          or @bandN 2_3
        #          or @bandN 1_6
        #          or @bandN -1
        items = list_lvl[i]['bandN'].split('_')
        for item in items:        
            if item not in lvl_band:
                lvl_band.append( int(item) )
                                
        pass
     
    bandN_total = max( lvl_band ) - min( lvl_band ) + 1
    
    # analyze the number of the levels
    for i in range( len( list_lvl ) ):
        item = list_lvl[i]['lvlE']
        if item not in lvl_eng:
            lvl_eng.append( float(item) )
            # we use int (instead of float) for the energy of a level.
        pass
   
    return bandN_total, min( lvl_band ), max( lvl_band ), max( lvl_eng ), min( lvl_eng )


def check_min_xi_xf_for_a_bandN( list_lvl, bandNtotal, band_largest ):
   
    # the index mean the bandN

    # list_bandL is to store the largest left  bound (xi) in a given bandN.
    # list_bandU is to store the smaller right bound (xf) in a given bandN.
    #   -----------------      
    #   |               |
    # bandL           bandU
    #
    num = bandNtotal
    if( (band_largest+1) > bandNtotal): num = band_largest+1
    list_bandL = [ -1   for _ in range( num ) ] 
    list_bandU = [ 9999 for _ in range( num ) ] 

    # the list index corresponds to the bandN
    # if we have bandN from -2, -1, 0, to 4.
    # [ 0,  1,  2,  3,  4,  -2,  -1]
    # if we have bandN from  5, 6, 7. bandNtotal = 3, but band_largest = 7
    # [ 0,  1,  2,  3,  4,  5,  6,  7] 
    

    for lvl in list_lvl:
        # set short-handed notations.
        xi = lvl['xi']
        xf = lvl['xf']
        bandL = lvl['bandL']
        bandU = lvl['bandU']

        if( xi >  list_bandL[ bandL ] ): list_bandL[ bandL ] = xi
        if( xf <  list_bandU[ bandU ] ): list_bandU[ bandU ] = xf
    
    return list_bandL, list_bandU





class Fine_parameter( ):
    def __init__( self, setupfile ):

        #default values
        self.bandwidth = 20
        self.bandspacing = 5
        self.outformat = 'PS'
        self.fontsize = 70 
        self.smallestFontSize=25
        self.auxlineExt = 0
        self.arrowAdjust = 1.00   
        self.minorShift = 0.1
        self.lvlDigit = 0
        self.lvlEngYOffset = 0.0
        self.lvlSpinYOffset = 0.0
        self.gamLabeLXOffset = 0.0
        self.gamLabeLYOffset = 0.0
        self.gamLabeLXLinear = 1.0
        self.gamLabeLYLinear = 1.0
        self.auxBandLimit = 1  
        self.lvlshrink = 0.2
        self.arrowLength = 0.5 
        self.gamCrosstxtRot = 1
        self.cornerxmin = 0.2
        self.cornerymin = 0.2
        self.cornerxmax = 0.13
        self.cornerymax = 0.975
        self.openXmgrace = 1
        self.outputWidth = 800  
        self.outputHeight = 600
        self.verbose = 1
        self.lvlLabelSplit = 0.

        # start parsing
        self.parse( setupfile )
        pass

    def parse( self, setupfile ):
        lines = [] 
        
        with open( setupfile ) as f:
            tmp_lines = f.readlines()

        # ignore the line start with '#'
        for line in tmp_lines:
            if( line[0].lstrip() != '#' ): lines.append( line )

        for line in lines:
            if( line.find( 'bandwidth' ) != -1 ): 
                self.bandwidth = int( self.get_value( line ) )
            elif( line.find( 'bandspacing' ) != -1 ): 
                self.bandspacing = int( self.get_value( line ) )
            elif( line.find( 'outformat' ) != -1 ): 
                self.outformat = str( self.get_value( line ) )
            elif( line.find( 'fontsize' ) != -1 ): 
                self.fontsize = int( self.get_value( line ) )
            elif( line.find( 'smallestFontSize' ) != -1 ): 
                self.smallestFontSize = int( self.get_value( line ) )
            elif( line.find( 'auxlineExt' ) != -1 ): 
                self.auxlineExt = int( self.get_value( line ) )
            elif( line.find( 'arrowAdjust' ) != -1 ): 
                self.arrowAdjust = float( self.get_value( line ) )
            elif( line.find( 'minorShift' ) != -1 ): 
                self.minorShift = float( self.get_value( line ) )
            elif( line.find( 'lvlDigit' ) != -1 ): 
                self.lvlDigit = int( self.get_value( line ) )
            elif( line.find( 'gamLabeLXOffset' ) != -1 ): 
                self.gamLabeLXOffset = float( self.get_value( line ) )
            elif( line.find( 'gamLabeLYOffset' ) != -1 ): 
                self.gamLabeLYOffset = float( self.get_value( line ) )
            elif( line.find( 'auxBandLimit' ) != -1 ): 
                self.auxBandLimit = int( self.get_value( line ) )
            elif( line.find( 'lvlshrink' ) != -1 ): 
                self.lvlshrink = float( self.get_value( line ) )
            elif( line.find( 'gamLabeLXLinear' ) != -1 ): 
                self.gamLabeLXLinear = float( self.get_value( line ) )
            elif( line.find( 'gamLabeLYLinear' ) != -1 ): 
                self.gamLabeLYLinear = float( self.get_value( line ) )
            elif( line.find( 'arrowLength' ) != -1 ): 
                self.arrowLength = float( self.get_value( line ) )
            elif( line.find( 'gamCrosstxtRot' ) != -1 ): 
                self.gamCrosstxtRot = int( self.get_value( line ) )
            
            elif( line.find( 'openXmgrace' ) != -1 ): 
                self.openXmgrace = int( self.get_value( line ) )
            elif( line.find( 'cornerxmin' ) != -1 ): 
                self.cornerxmin = str( self.get_value( line ) )
            elif( line.find( 'cornerymin' ) != -1 ): 
                self.cornerymin = str( self.get_value( line ) )
            elif( line.find( 'cornerxmax' ) != -1 ): 
                self.cornerxmax = str( self.get_value( line ) )
            elif( line.find( 'cornerymax' ) != -1 ): 
                self.cornerymax = str( self.get_value( line ) )

            elif( line.find( 'outputWidth' ) != -1 ): 
                self.outputWidth = float( self.get_value( line ) )
            elif( line.find( 'outputHeight' ) != -1 ): 
                self.outputHeight = float( self.get_value( line ) )

            elif( line.find( 'verbose' ) != -1 ): 
                self.verbose = int( self.get_value( line ) )

            elif( line.find( 'lvlEngYOffset' ) != -1 ): 
                self.lvlEngYOffset = float( self.get_value( line ) )

            elif( line.find( 'lvlSpinYOffset' ) != -1 ): 
                self.lvlSpinYOffset = float( self.get_value( line ) )
         
            elif( line.find( 'lvlLabelSplit' ) != -1 ): 
                self.lvlLabelSplit = float( self.get_value( line ) )

            pass    
        
        pass

    def get_value( self, line ):
        items = line.split('=')
        values = items[1].split()
        return values[0]


if __name__ == '__main__':
     
    pass
 



