#!/usr/bin/python3.4
import mytool
import xmgrace_plot 
import subprocess           # for calling xmgrace to plot.
import sys

 

def print_message():
    outstr = """
 format:

 ./lvl_builder inputfile [fineParameter.txt] [output.agr]

 the "fineParameter.txt" and "output.agr" are optional arguments.

 "fineParameter.txt" for the fine control of presentaion details. """
    print( outstr )
    print("""
    __________________________________
    |                                |
    |    Written by Pei-Luan Tai,    |
    |    v1 2017, Nov 13             |
    |________________________________|
    """)




def lvl_builder():
    
    dataFile = "demo_general_properties.txt"
    fineControlFile = "fineParameter.txt"   
    outputAgr = "output.agr"
    
    hasTextLabel = False # True, only if we include bandTextFile from cmd line.
    bandTextFile = ""
    
    cmd = 'rm ' + outputAgr + ' 2>/dev/null'
    subprocess.call( cmd, shell=True ) 

    if( len(sys.argv) == 2  ):
        if( sys.argv[1] == '-h' or sys.argv[1]=='--help' ):
            print_message()
            sys.exit( 0 )
        else:
            dataFile    = sys.argv[1]
    elif(len(sys.argv) == 3  ):
        dataFile        = sys.argv[1]
        fineControlFile = sys.argv[2]
    elif(  len(sys.argv) == 4  ):
        dataFile        = sys.argv[1]
        fineControlFile = sys.argv[2]
        outputAgr       = sys.argv[3]
    elif(  len(sys.argv) == 5  ):
        dataFile        = sys.argv[1]
        fineControlFile = sys.argv[2]
        outputAgr       = sys.argv[3]
        bandTextFile    = sys.argv[4] 
        bandText = xmgrace_plot.BandText()
        hasTextLabel = True
    else:
        print_message()
        sys.exit( 0 )

    par = mytool.Fine_parameter( fineControlFile )
    if( par.verbose): print( " input file = ", dataFile )
    if( par.verbose): print( " fine paraters = ",  fineControlFile )
    if( par.verbose): print( " output agr = ", outputAgr)
    
    
    #=================================================
     
    list_lvl = []
    list_gam = []
    list_lvl, list_gam = mytool.readin_data( dataFile )  
    outfile = open( outputAgr ,'w')  
    

    # width set up 
    #  5      10      5          
    #^^^^^==========^^^^^
    # total = 20
    band_width = par.bandwidth
    band_spacing = par.bandspacing
    font_size = par.fontsize
    
    
    #
    # get the band structure info
    # each element in list_lvl is a dic,
    # and its  keys: 'bandN', 'lvlE', 'color', 'spin'
    # 
    # check_total_bands function will give us (1) total band number
    # (2) smallest band index, to serve as the starting index
    # (3) the max and min level energies, setting the y min/max range for xmgrace. 

    band_totalN, band_smallest, band_largest, band_max_eng, band_min_eng \
    = mytool.check_total_bands(list_lvl) 
    
    
    
    #
    #  the font size calculation. 
    #  The font size varies corresponding to the total band numbers. 
    #  The smallest font size is set by smallestFontSize.
    #
    if band_totalN * band_width > 80:
        font_size = int( font_size * 100./ band_totalN/band_width )
        if font_size < par.smallestFontSize: 
            font_size = par.smallestFontSize
        #note: 100 is just my emperical value.
        
        
    
   

    # in this step, we adjust the height for the text such that
    # there is no overlapped text labels for two or more closed states.
    # 
    # 'textY' key is for the text height, and it may be different
    # than the level y position ( by 'lvlE' key )
    # 'overlap' and 'olap_lvl' keys are added for processing. 
    length = float(band_max_eng)- float(band_min_eng) # for y
    dim = ( length, font_size, par.lvlLabrlSplit )
    pre_parse_lvl = xmgrace_plot.PRE_Separate_levels( list_lvl, dim )
    agrYmin, agrYmax = pre_parse_lvl.Get_textY_min_max()




    # use the Predefine_agr class object "agr_setup" to help us
    # control the output of the agr. 
    # this step is to set the x and y dimension
    # band_totalN control the x dimension, text height for the y dimension.
    Xrange =  band_totalN  * ( band_width + 2* band_spacing )
    
    agr_setup \
    = xmgrace_plot.Predefine_agr (par, 0, agrYmin , Xrange, agrYmax  ) 
  
    outfile.write( agr_setup.preSection() )  
    outStr= ""



    
    # to plot the levels
    # we add key: 'xi' and 'xf' to each dic element in list_lvl, 
    # in Update() method.
    band_info = ( band_smallest, band_width, band_spacing )
    dim = (length)
    for lvl in list_lvl:
        obj_temp = xmgrace_plot.Level( lvl, band_info, dim )
        obj_temp.Set_fontsize( font_size )
        obj_temp.Set_par( par ) 
        outStr += obj_temp.Process() 
        obj_temp.Update( lvl) # get the position xi and xf 
        pass
    
    # since some lvls could shrink, so we have to do some calcuations
    # for the max bandL and min bandU for a given bandN
    list_bandL, list_bandU = \
    mytool.check_min_xi_xf_for_a_bandN( list_lvl, band_totalN, band_largest )
    

    #  each element in list_gam is a dic,
    #  original keys: 'Ef', 'Ei', 'label', 'I', and 'color'
    pre_parse = xmgrace_plot.PRE_Parse_gamma_level( list_lvl, \
                                                    list_gam, \
                                                    list_bandL, \
                                                    list_bandU, \
                                                    par )





    list_lvl, list_gam = pre_parse.Update()
    
    # after pre_parse we add key for a gam: 
    # 'xi', 'xf', 'Ei' and 'Ef' (used for final plot) 
    # 'crossBand' maps to a boolean value.
    # 
    #  several keys for calculations.
    # 'Ei_xi', 'Ei_xf', 'Ef_xi', 'Ef_xf' 
    # 'overlap_range_xi', 'overlap_range_xf'
    # 'overlap'  
    #
    
    
    
    # to plot the gammas

    dim = ( float(band_min_eng), float(band_max_eng),\
            float( band_totalN*band_width) )
    for gam in list_gam:
        obj_temp = xmgrace_plot.Gamma( gam, list_lvl, dim )
        obj_temp.Set_par( par ) 
        obj_temp.Set_fontsize( font_size )
        outStr += obj_temp.Process()
        pass
            
    
    # to plot text lables
    if( hasTextLabel ):
        dim = ( band_smallest, band_width, band_spacing, font_size, length )
        outStr += bandText.parse( bandTextFile, dim )
        pass


    outfile.write( outStr ) # write out result to agr file.
    
    outfile.write( agr_setup.postSection() ) # for the xmgrace ending section.
    outfile.close()
    
    #=======================================================================
    # generate output file
    #

    if( par.openXmgrace ):
        subprocess.call( 'xmgrace ' +  outputAgr + '    &', shell=True )
    
    outputfile = ""
    cmd = ""
    if( outputAgr[-4:] == '.agr' ): outputfile = outputAgr[:-4]
    else: outputfile = outputAgr
    

    if( par.outformat.upper() == 'PNG'): 
        outputfile += ".png"
        cmd = 'xmgrace '+ outputAgr + \
          ' -hardcopy -printfile "'+outputfile+'" -hdevice PNG'

    elif( par.outformat.upper() == 'PS' ):
        outputfile += ".ps"
        cmd = 'xmgrace '+ outputAgr + \
          ' -hardcopy -printfile "'+outputfile+'" -hdevice PostScript'
    
    elif( par.outformat.upper() == 'EPS'):
        outputfile += ".eps"
        cmd = 'xmgrace '+ outputAgr + \
          ' -hardcopy -printfile "'+outputfile+'" -hdevice EPS'
    
    subprocess.call( cmd, shell=True )
    if(par.verbose): print( " output     = ", outputfile)    

    return 1

if __name__ == '__main__':
    lvl_builder()
