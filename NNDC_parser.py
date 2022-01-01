import requests
import re
from bs4 import BeautifulSoup
import pdb


class NNDCParser():
    
    def __init__(self):
        """
        feed method is our entry where we start to get the table, and it will
        break down the table row by row, each row will be send to
        'parse_a_row' to extract the energy, spin, gammas.But we have to deal
        with the last row indiviually.
        
        the data structure
        levels[ level1, level2, level3 ]
        
        level={}
        level['Ex']= float, energy of a level
        level['Ex_err']   = float, error of the enery
        level['ref'] = list, each element is string, ex 'A', 'B' 
        level['spin']     = str, "3/2+"
        level['lifetime'] = str
        level['lifetime_unit'] = str
        level['lifetime_err'] = str
        level['lifetime_sec'] = float
        
        level['gammas'] = [ gamma1, gamma2, ... ]
        gamma = {}
        gamma['eng'] = float, gamma energy
        gamma['err'] = float, gamma energy err
        gamma['?']   = bool,  not certrain
        gamma['I']   = str, relative intensity ( having <50 ..format)
        gamma['I_err'] = str, relative intensity error
        
        level['final_states'] = [ float, float, ...]
        
        one can use print_result method to check the data.
         
        """
        self.__levels = []
        self.__col_Dict={}
        self.refs = {}
        pass
    
    def feed(self, content ): 
        """ to extact the each raw from the table, 
        and then pasre the data in a row. """

        # foward the data to the table with levels and gammas
        marker = "<TABLE cellspacing=1 cellpadding=4 width=800>"
        idx_tmp    = content.find(marker)
        length_tmp = len( marker )
        refs = content[ : idx_tmp ]
        self.__parse_refs( refs )
        content = content[ idx_tmp+length_tmp:  ]
        
        marker  = "</table>"
        idx_tmp = content.find(marker)
        content = content[ :idx_tmp ] + "</table>"
          
        # In general, we have multiple rows in the table.
        # only the first row have the close tag "</tr>"
        # other row just open tab <tr>
        tag_tr_i = "<tr"
        tag_tr_m = ">"
        tag_tr_f = "</tr>"
        
        idx_tr_i = content.find( tag_tr_i ) 
        idx_tr_m = content.find( tag_tr_m, idx_tr_i ) 
        idx_tr_f = content.find( tag_tr_f, idx_tr_m  ) 
        
        
        # check if we do find the tag.
        go_on = (idx_tr_i != -1 and idx_tr_m != -1 and  idx_tr_f != -1 )
        
        # cut the first row off, it is the table header
        # we need to parse the header, the column content is not 
        # always in the same order. 
        if( go_on ):
            idx2 = idx_tr_f + len( tag_tr_f )
            header  = content[ :idx2 ]
            self.__parse_header(header)  # header analysis.
            content = content[ idx2: ] # the rest data.
             
        
           
        # the rest rows are having a single <tr> without </tr>
        # so we need to reset the tag_tr_i to '<tr>' from '<tr'
        tag_tr_i = "<tr>"
        while ( go_on ):
            # since no </tr> close tag, 
            # I can only search for next <tr> as a marker.
            # and let the  <tr> .... <tr> ..... structure as our go_on indication.
            # In this way, we will miss the last row.
            # Hence, we have to deal with the last row latter.
            idx1 = content.find( tag_tr_i ) 
            idx2 = content.find( tag_tr_i, idx1 + len(tag_tr_i) )

            if( idx1 == -1 or idx2 == -1):             
                go_on = False
                 
            else:                 
                aRowData = content[ idx1 + len( tag_tr_i ): idx2 ]

                if re.search( r'colspan="\d+"', aRowData):  
                    pass
                    # this is just a comment block.
                else:  
                    # append the return from parse_a_row to our __levels list. 
                    self.__levels.append( self.parse_a_row( aRowData )  )

                               
                # forward the content to next row.                   
                content = content[ idx2: ]
                
                #print("\n", content.replace("&nbsp;","") )# for testing.

                
        # deal with the last row.       
        tag_tr    = "<tr>"
        tag_table = "</table>"
        idx_tr    = content.find( tag_tr )
        idx_table = content.find( tag_table )
        lastRow   = content[ idx_tr + len(tag_tr): idx_table ]
        self.__levels.append( self.parse_a_row( lastRow ) )
        #print( lastRow.replace("&nbsp;","") ) 
                     
        pass   
            
    def __parse_refs( self, data ):
        "to parse a table with 4 columns"
        
        # take off <table> tag.
        marker1 = "<table cellspacing=1>"
        marker2 = "</table>"
        idx1 = data.find( marker1 )
        idx2 = data.find( marker2, idx1 )
        data = data[ idx1+len(marker1): idx2 ]
        
        # only first row and last row have </tr> tag.
        tag_tr_i = "<tr>"
        tag_tr_f = "</tr>"
        go_on = True
        
        while( go_on ):
            idx_tr_i = data.find( tag_tr_i ) 
            idx_tr_f = data.find( tag_tr_f, idx_tr_i ) 
            
        
            if( idx_tr_i == -1 and idx_tr_f == -1  ):
                go_on = False
            else:                 
                aRow = data[ idx_tr_i + len(tag_tr_i): idx_tr_f ]               
                self.__ref_aRow( aRow ) # self.refs will be updated here.
                data = data[ idx_tr_f: ]
           
         
               
    
    def __ref_aRow(self, data ):
        tag_i = "<td"
        tag_f = "</td>"
        go_on = True
        
        tmp = []
        
        if( data.find("References") != -1 ): return
        
        while( go_on ):
            idx_i = data.find( tag_i ) 
            idx_f = data.find( tag_f, idx_i ) 
            
        
            if( idx_i == -1 and idx_f == -1  ):
                go_on = False
            else:
                 
                aCol = data[ idx_i + len(tag_i): idx_f ]
                aCol = aCol.replace("align=left nowrap>","")
                aCol = aCol.replace("align=center>","")
                aCol = aCol.replace("&nbsp;","")
                aCol = aCol.replace("<sup>","")
                aCol = aCol.replace("</sup>","")
                aCol = aCol.replace("&alpha;","a")
                aCol = aCol.replace("&beta;","b")
                aCol = aCol.replace("&gamma;","g")
                aCol = aCol.replace("&mu;","g")
                aCol = aCol.replace("&rsquo;","'")
                tmp.append( aCol )
                
                data = data[ idx_f: ]
            #--------------------------------end of while
        
        # assign data to self.refs
        # note: we have the following structure.
        #[' I', ' 28Si(18O,15O)', ' J', ' 31P(g-,NU)']
        # [' K', ' 31P(n,p)', ' ']
        sizeN = len( tmp )//2 * 2 
        for i in range( 0, sizeN, 2  ):
            tag = tmp[i]
            string = tmp[i+1]
            xx = re.search(r'<a href=.*target="_blank">(.*?)</a>', string)
            if xx: string = xx.group(1)
            self.refs[ tag ] = string
 
        pass

    def __parse_header(self, header ):
        """
        we have data look like:
        <tr><td class="header">E(level)<br>(keV)</td><td class="header">XREF</td>
            <td class="header">J&pi;(level)</td><td class="header"> T<sub>1/2</sub>(level)</td>
            <td class="header">E(&gamma;)<br>(keV)</td><td class="header">I(&gamma;)</td>
            <td class="header">M(&gamma;)</td><td  class="header" colspan=2>Final level  </td>
        </tr>
        and we have to parse to know which column corresponds to which type of data.
        we assign it into self.
        The data will be stored at self.__col_Dict
        """
        tag_tr_i = "<tr>"
        tag_tr_f = "</tr>"
        idx_tr_i = header.find( tag_tr_i )  
        idx_tr_f = header.find( tag_tr_f, idx_tr_i  ) 
        
        # remove the outermost <tr> and </tr> tags.
        header = header[ idx_tr_i+len(tag_tr_i) : idx_tr_f ]

        # we have two possible tags, with/withoug "colspan=2"
        tag_td_i  = '<td class="header">'
        tag_td_i2 = '<td  class="header" colspan=2>'
        
        tag_td_f = "</td>"
        go_on = True
        col = 1        
         
        while ( go_on ):            
            # search <td> ... </td> tags.
            idx1A = header.find( tag_td_i ) 
            idx1B = header.find( tag_td_i2 ) 
            idx2  = header.find( tag_td_f, idx1A + len(tag_td_i) )
             
            if( idx2 == -1):  
                go_on = False
               
            else:
                # to get a column data 
                if( idx1A != -1  ):
                    aColData = header[ idx1A + len( tag_td_i ): idx2 ]
                    
                elif( idx1B != -1 ): 
                    aColData = header[ idx1B + len( tag_td_i2 ): idx2 ]
                
                # assign which col to which type of data.
                if( aColData.find('E(level)') != -1 ): self.__col_Dict[ "Ex" ] = col 
                elif( aColData.find('XREF') != -1 ):   self.__col_Dict[ "XREF" ] = col 
                elif( aColData.find('J&pi') != -1 ):   self.__col_Dict[ "Jpi" ] = col 
                elif( aColData.find('T<sub>1/2</sub>') != -1 ): self.__col_Dict[ "T" ] = col 
                elif( aColData.find('E(&gamma;)') != -1 ):   self.__col_Dict[ "gamma"] = col 
                elif( aColData.find('I(&gamma;)') != -1 ):   self.__col_Dict[  "I" ] =  col
                elif( aColData.find('M(&gamma;)') != -1 ):   self.__col_Dict[ "M" ] = col 
                elif( aColData.find('Final level') != -1 ):  self.__col_Dict[ "flevel" ] = col 
                else:
                    print( aColData )
                                
                # forward the content to next col.                   
                header = header[ idx2: ]
                col += 1
    

    def parse_a_row(self, aRowData ):
        """ to parse data in <tr> ... </tr>, which I call a row.
            In a row, we have multiple <td>...</td> tags,  which I call cells.
            In some cases, the last row only has the <td> but no </td> tag. 
        """
         
        # define a dictionary object 'level', and we will return it,
        # which will be appended into self.__levels
        level = {}

        level['?'] = False  # default, a level is not uncertain. 
        Ex_status = True    # for excitation energy level
        go_on = True
        col_idx = 0  # for col index.


        tag_td_i = "<td"
        tag_td_m = ">"
        tag_td_f = "</td>"
        

        while ( go_on ):
            idx1 = aRowData.find( tag_td_i ) 
            idxm = aRowData.find( tag_td_m, idx1 ) 
            idx2 = aRowData.find( tag_td_f, idx1 + len(tag_td_i) + 1 )
             
            if( idx1 == -1 or idx2 == -1):                 
                go_on = False
                # when we cannot find <td> .... </td> structure  
                # we will exist the loop.
                
            else:   
                col_idx += 1
             
                # to analyze a cell   
                cellData = aRowData[ idxm + 1: idx2  ]
                cellData = cellData.replace( "&nbsp;", "")

             
                # the Ex cell also serves as a filter,
                # only when Ex is ok, we extract the other properties of this level.
                if( "Ex" in self.__col_Dict and col_idx == self.__col_Dict["Ex"] ):
                   
                    Ex_status = self.check_Ex( cellData ) 
                                   
                    if( Ex_status ):
                        level['Ex'], level['Ex_err'] = \
                        self.get_Ex_and_Err( cellData, level['?']  )  
                        # Ex, and Ex_err will update through return value,
                        # '?' will be update in this place.
                    
               
                
                 
                if( "XREF" in self.__col_Dict and col_idx == self.__col_Dict["XREF"] and Ex_status  ):
                    level['ref'] = self.__parse_XREF( cellData ) 
                          
                
                 
                if( "Jpi" in self.__col_Dict and col_idx == self.__col_Dict["Jpi"] and Ex_status  ):
                    
                    cellData = cellData.replace(" ","")
                    cellData = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', cellData )
                    cellData = re.sub( r'</a>', '', cellData )
                    # if( cellData == "" ): cellData = "NA"
                    level['spin'] = cellData
  
                 
                if( "T" in self.__col_Dict and col_idx == self.__col_Dict["T"] and Ex_status ):
                     
                    level['lifetime'], level['lifetime_unit'], level['lifetime_err'], \
                    level['lifetime_sec'] \
                    = self.get_lifetime( cellData )


                 
                if( "gamma" in self.__col_Dict and col_idx == self.__col_Dict["gamma"] and Ex_status ):
                    level['gammas'] = self.get_gammas( cellData ) 


                
                if( "I" in self.__col_Dict and col_idx == self.__col_Dict["I"] and Ex_status ):
                    self.get_relative_intensity( cellData, level['gammas'] ) 
                    
                     

                if( "flevel" in self.__col_Dict and col_idx == self.__col_Dict["flevel"] and Ex_status ):        
                    level['final_states'] = self.get_final_states( cellData )
                    pass

                aRowData = aRowData[ idx2 + len(tag_td_f) : ]
                
                if(0): print("TEST", col_idx , cellData )
                if(0): print( aRowData )
                
                
                
         
    
        return level
    
    
    def check_Ex(self, Ex_string ):
        """ we ignore the states from unplaced band head, which Ex_status = False
        """
        Ex_status = True
        if( Ex_string[0]=="("  and Ex_string[-1]==")" ): Ex_status = False
        
        symbols = ( "A", "B", "C", "D", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" )
        
        for sym in symbols:
            if( len(Ex_string) == 1  and (Ex_string.find( sym ) != -1) ):
                Ex_status = False
            
            sym = "+"+sym
            if( len(Ex_string) > 1   and (Ex_string.find( sym ) != -1) ):
                Ex_status = False
                pass

        if( Ex_string.find( "&ge" ) != -1 ): Ex_status = False
        if( Ex_string.find( "&gt" ) != -1 ): Ex_status = False
        if( Ex_string.find( "&lt" ) != -1 ): Ex_status = False
        if( Ex_string.find( "SP" )  != -1 ): Ex_status = False
        if( Ex_string.find( "Syst.")!= -1 ): Ex_status = False
        return Ex_status
        
        
        
    
    def get_Ex_and_Err(self, data, uncertain):
        """ to extract the excitation energy and error from data,
            normally, it has format as 1000 2,
            the second number is uncertainty.
        """
        Ex = -1. ; err = -1.
        data_ori = data
        data = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', data )
        data = re.sub( r'</a>', '', data )      
         
        items = data.split(" ")
        
        #  Ex part.
        Ex = items[0]
        Ex = Ex. replace( "S", "" )  #ex. 6587.40 4 S
        
        try:
            Ex[-1]
        except:
            pdb.set_trace()

        # if we have 1000? 
        if( Ex[-1] == "?" ):
            uncertain = True
            Ex = Ex.replace( "?", "" )
        
        # if we have ~1000    
        if( Ex.find("&asymp;") != -1 ):
            # remove the approximation sign.
            Ex = Ex. replace( "&asymp;", "" )

        # Ex err part
        if ( len(items) > 1):
            
            # use this condition to make sure we do have uncertainty term.
            # the err has the <i> </i> tags.
            err = items[1]
            err = err.replace("<i>", "")
            err = err.replace("</i>", "")
            err = err.replace("S", "")
            
            if( err[-1]=="?" ):
                uncertain = True
                err = err.replace("?", "")
                           
        err = float( err )
        Ex  = float ( Ex )
        return Ex, err
    
    def __parse_XREF( self, data ):
        tag_a_i = "<a"
        tag_a_m = '">'
        tag_a_f = "</a>"
        go_on = True
        refs = []
         
        while( go_on ):
            idx1 = data.find( tag_a_i ) 
            idxm = data.find( tag_a_m, idx1 ) 
            idx2 = data.find( tag_a_f, idx1 + len(tag_a_i) + 1 )
            
            if( idx1 == -1 or idx2 == -1):     
                go_on = False
            else:
                refTemp = data[ idxm+len(tag_a_m): idx2 ]
                refs.append( refTemp )                
                 
                data = data[ idx2: ] # to forward
    
        return refs
        
          

    def __lifetime_to_sec(self, lifetime, unit):
        """ doing the unit conversion, and make lifetime in unit of second"""
        if( unit == "" ):  return 0.
        if( lifetime == "" ): return 0. 
        if( unit.find("eV") != -1 ): return 0. 
        if( lifetime.find("<")  != -1 ): return 0.
        
        unit_s = 0.0
        if( unit == "s" ): unit_s = 1.
        elif( unit == "m" ): unit_s = 1. * 60.
        elif( unit == "h" ): unit_s = 1. * 60. * 60.
        elif( unit == "d" ): unit_s = 1. * 60. * 60. * 24.
        elif( unit == "y" ): unit_s = 1. * 60. * 60. * 24. * 365.
        elif( unit == "ms" ): unit_s = 1.E-3
        elif( unit == "&micro;S" ): unit_s = 1.E-6
        elif( unit == "ns" ): unit_s = 1.E-9
        elif( unit == "ps" ): unit_s = 1.E-12
        elif( unit == "fs" ): unit_s = 1.E-15
        elif( unit == "as" ): unit_s = 1.E-18
        else:
            print( "TEST", unit )
                
        lifetime_sec = 0.0
        try:
            lifetime_sec = float( lifetime )
        except:
            pass
        
        lifetime_sec = lifetime_sec * unit_s
        return lifetime_sec 
         


    def get_lifetime(self, data):
        """
        note: we can have the following format.
        157.36 m <i>26</i> <br>  % &beta;<sup>-</sup> = 100 <br>  
        """
        data = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', data )
        data = re.sub( r'</a>', '', data )

        # To skip the second raw, such as % p = 99.
        data1 = data.split("<br>")[0]
        
        
        lifetime = "0.0"
        lifetime_unit = ""
        lifetime_err = "0.0"

        if( data1.find("&lt;") != -1 or \
            data1.find("&gt;") != -1 or \
            data1.find("&le;") != -1 or \
            data1.find("&ge;") != -1 ): 
            
            items = data1.split(" ")

            # ['', '&lt;', '5.0', 'ns', '']
            if( len(items) > 1 ):
                lifetime = "<" + items[2]
                lifetime_unit = items[3]

        elif( data1.find("asymp;") != -1 ): 
            
            items = data1.split(" ")
             
            # ['', '&asymp;', '0.5', 'ns', '']
            if( len(items) > 1 ):
                lifetime = "<" + items[2]
                lifetime_unit = items[3]

        else:
            items = data1.split(" ")
            if ( len(items) > 3):
                lifetime      = items[1]
                lifetime_unit = items[2]
                lifetime_err  = items[3]
                lifetime_err = lifetime_err.replace("<i>", "")
                lifetime_err = lifetime_err.replace("</i>", "")

        if( data1.find("%") != -1 ):
            lifetime = "0.0"
            lifetime_unit = ""
            lifetime_err = "0.0"
            
        
        lifetime_sec = self.__lifetime_to_sec( lifetime, lifetime_unit )
        return lifetime, lifetime_unit, lifetime_err, lifetime_sec      
    
    
    
    def get_gammas(self, data):
        
        """ parse the gamma info, we data looks like: 
            943.2 <i>7</i><br>1694.87 <i>5</i><br>
            it contins multiple gammas.
            
            rare cases:
            5 <i>Calc.</i>S<br> .... 
        """
        gamma_infos = []
    
        data = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', data )
        data = re.sub( r'</a>', '', data )
              
        items = data.split("<br>")
        # the last one is "", 
        # so I require at least have one gamma.
        if( len(items)>1 ):
            for item in items:
                
                if( item.find("Calc") != -1 ):
                    # not include the calculated one.
                    pass
                elif( len(item)>1):
                    # the len(item) condition is to ignore the last ""
                    gamma_infos.append( item )
                pass
            pass
        
        
        # now we have a list
        # [ '943.2 <i>7</i>', '1694.87 <i>5</i><br>']
        gammas = []
        
        for gamma_info in gamma_infos:
            gamma = {}
            gamma['?'] = False
            gamma_eng = ""
            gamma_err = 0
            
            
            items = gamma_info.split()
            if( len(items) > 1):
                # enery part
                gamma_eng = items[0]
                
                if( gamma_eng[-1] == "?"   ): 
                    gamma['?'] = True
                    gamma_eng = gamma_eng.replace( "?", "")
                   
                
                
                gamma_err = items[1]
                if( gamma_err[-1] == "?"): 
                    gamma['?'] = True
                    gamma_err = gamma_err.replace( "?", "")
                gamma_err = gamma_err.replace("<i>", "")
                gamma_err = gamma_err.replace("</i>", "")
                gamma_err = gamma_err.replace( "S", "")
                
            elif( len(items) == 1):
                
                gamma_eng = items[0]
                gamma_eng = gamma_eng.replace( "&asymp;", "")
                
                 
                if( gamma_eng[-1] == "?" or gamma_eng[-1] == ")" ): 
                    gamma['?'] = True
                    gamma_eng = gamma_eng.replace( "?", "")
                    gamma_eng = gamma_eng.replace( "(", "")
                    gamma_eng = gamma_eng.replace( ")", "")
             
            gamma_eng = gamma_eng.replace( "S", "") # 0+ --> 0+
            
            try:
                gamma_eng = float( gamma_eng )
                gamma_err = float( gamma_err )
            except:
                pdb.set_trace()
            gamma['eng'] = gamma_eng
            gamma['err'] = gamma_err
            gammas.append( gamma )
        
        return gammas
        pass
    
    
    def get_relative_intensity(self, data, gams ):
        """
        we have data look likes:
        100<br>
        1.01 <i>25</i><br>100 <i>5</i><br>
        18 <i>4</i><br>22 <i>6</i><br>100 <i>8</i><br>
        16 <i>6</i><br>&lt;3.5<br>&lt;3.5<br>100 <i>6</i><br>
        """

        data = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', data )
        data = re.sub( r'</a>', '', data )
        
        items = data.split("<br>")
        if len( items ) <= 1: return 0
        if( "" in items ): items.remove("")
        if( len(items) != len(gams) ): return 0
         
        cnt = 0
        for item in items:
            # ignore the empty one.
            if( item == "" ): continue
            if( item.find("<i>") != -1 ):
                things = item.split(" ")
                
                gams[cnt]['I'] = things[0]
                I_err = things[1]
                I_err = I_err.replace("<i>", "")
                I_err = I_err.replace("</i>", "")
                gams[cnt]['I_err']= I_err
                
                cnt += 1                 
            else:
                #just single value or with "<"
                gams[cnt]['I_err'] = ""
                if( item.find("&lt;") != -1 ):  
                    things = item.split( "&lt;" )              
                    gams[cnt]['I'] = "<" + things[1]
                    if(0): print( gams[cnt]['I']  )
                else:
                    gams[cnt]['I'] = item.rstrip()                     
                cnt += 1


    
    def get_final_states( self, data ):
        """
        we data looks like:
        2316.93<br>1694.91<br>752.23<br>0<br>
        """
        finalSates = []

        data = re.sub( r'<a.*?onmouseout="UnTip\(\)">', '', data )
        data = re.sub( r'</a>', '', data )
        items = data.split("<br>")
        
        # the last term = "", so I requre at least 2 items.
        if( len(items)>1 ):
            for item in items:
                # in some case we will empty one.
                if( item != ' ' and len(item) >= 1 ):
                    #item = item.replace("+X", "")
                    #item = item.replace("+Y", "")
                    #item = item.replace("+Z", "")
                    item = float(item )
                    finalSates.append( item )
            
        return finalSates
  


    def get_levels(self): return self.__levels

    def print_levels(self, upperLimt=9999999.0):
        """by default, we will print all the levels,
        use upperLimt is in unit of keV. """

        outStr = ""
        
        for level in self.__levels:
            if( level['Ex'] <= upperLimt  ):
                if( 'spin' not in level or level['spin'] == "NA" ):
                     s = "@lvlE %7.3f " %(level['Ex'] )
                else:
                    s = "@lvlE %7.3f @spin %s "\
                    %(level['Ex'], level['spin'] )
                
                outStr += s
                outStr += "\n"
                
                # deal with the final state(s)
                #'final_states' are the states the gammas decay to
                if( 'final_states' in level.keys() and \
                    len(level['final_states'] )>1 ):
                    
                    gam_cnt = 0     
                    for final_state in level['final_states'] :
                        Ei = level['Ex']
                        Ef = final_state
                        gam = level['gammas'][gam_cnt]
                        gammaE = gam['eng']   
                        s = "@Ei %8.3f @Ef %8.3f @E %8.3f" %(Ei, Ef, gammaE) 
                         
                        outStr += s
                        outStr += "\n"
                        gam_cnt += 1

                s = ("#" + "="*78) # separation line.
                outStr += s
                outStr += "\n"
                
        print( outStr )
         
       
    def reset(self): 
        self.__levels = []; 
        self.__col_Dict = {}
        self.refs = {}
         
   