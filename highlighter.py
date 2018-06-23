#!/usr/bin/python3.4
import readline  
import subprocess
import sys
import os


class Highlighter():
    """ to highlight the levels and gammas. """
    
    def __init__(self, lvl_file ):
        '''
        read in input file lvl_file and pasre the data 
        into list_lvl and list_gam.
        '''    
        self.list_lvl,  self.list_gam = self.__get_lvl_gam( lvl_file )
         
        self.__lvlE_limit = -1  # the upper energy limit, use in presort. 

         
        self.__lvls_highlight = []
        self.__lvls_by_qualifed_gams = []   
        self.__lvls_no_gam = []
        self.lvlErange = 2
        self.gamErange = 2
        
        self.list_gam_new = []
        self.list_lvl_new = []
        
        self.__lvlE_limitU = 99999
        self.__lvlE_limitL = -1

        # plotting.
        self.__highlight_lvl = True
        self.__force_to_show_all_lvls = False
   

     
    def set_lvl_highlight(self, flag ): self.__highlight_lvl = flag;     
    def set_force_to_show_all_lvls(self, flag ): self.__force_to_show_all_lvls = flag;
    def set_lvlErange(self, eRange = 2.0 ): self.lvlErange = float(eRange);
    def set_gamErange(self, eRange = 2.0 ): self.gamErange = float(eRange);
 
    def set_lvlE_limit( self, ulimit=99999, llimit=-1 ):
        ''' set the upper and lower lvlElimit '''
        ulimit = float( ulimit )
        llimit = float( llimit )
        self.__lvlE_limitU = ulimit
        self.__lvlE_limitL = llimit

  
    def __get_lvl_gam(self, lvl_file ):
        """ to parse lvl_file and assign them to list_lvl and list_gam """
        try:
            readIn = open( lvl_file ,'r')     
        except IOError:
            print( "Error: %s does not exist." %lvl_file )
            sys.exit(0)

        lines = readIn.readlines()
    
        # --- ignore the commented line which starts with '#'
        newlines = []
        for line in lines:
            line = line.lstrip(' ')
            if line[0] != '#':
                newlines.append(line) 
        lines = newlines
        del newlines
        
        list_lvl = []
        list_gam = []
    
        for line in lines:
            lvl = {}
            gam = {}
            isLvl = False
            isGam = False
            elements = line.split('@')
            
             
            # pre-check a line to identify lvl or gam.
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
                for element in elements[1:]:        
                    mykey = element.split()[0]
                    myvalue = element.split()[1]
                    lvl[mykey] = myvalue
                list_lvl.append( lvl )
                
            if( isGam ):
                 
                for element in elements[1:]:        
                    mykey = element.split()[0]
                    myvalue = element.split()[1]
                    gam[mykey] = myvalue
                list_gam.append( gam )   
            
        return list_lvl, list_gam
    

    def pre_sort( self, lvlE_limitU = -1, lvlE_limitL = -1 ):
        ''' 
        to use limits to pre filter out the lvls and gams 
        '''
        if( lvlE_limitU != -1 and lvlE_limitL != -1 ):
            self.__lvlE_limitU = lvlE_limitU
            self.__lvlE_limitL = lvlE_limitL
         
        # for lvls
        lvls_temp = [] 
        # looping through original list_lvl, and seek those under the lvlE_limit
        for lvl in self.list_lvl:
            lvlE = float( lvl['lvlE'] )
            if( lvlE <= self.__lvlE_limitU and lvlE >= self.__lvlE_limitL ):
                lvls_temp.append( lvl )
        self.list_lvl = lvls_temp[:]
        del lvls_temp;


        # for gams
        gams_temp = []          
        for gam in self.list_gam:
            Ei = float( gam['Ei'] )
            Ef = float( gam['Ef'] )
            if( Ei <= self.__lvlE_limitU and Ef >= self.__lvlE_limitL ):
                gams_temp.append( gam )
        self.list_gam = gams_temp[:]

        del gams_temp;

    
    def __no_duplicate( self, items ):
        ''' remove duplicated items in a list '''
        items_test = []
        for item in items:
            if item not in items_test:
                items_test.append( item )
        return items_test[:]

     
    def __test_gam(self, gam, lvlE, useEi, useEf ):
        """ 
        to see whetehr Ei and Ef of a gam are within the range of a lvlE.
        self.__lvls_by_qualifed_gams will be also updated here.
        """
        lvlE = float( lvlE )
        Ei = float( gam['Ei'] )
        Ef = float( gam['Ef'] )
        lvlErange = self.lvlErange
        
        Ei_match = False
        Ef_match = False
         
        if( Ei>(lvlE-lvlErange) and  Ei<(lvlE+lvlErange) ):
            Ei_match = True
         
        if( Ef>(lvlE-lvlErange) and  Ef<(lvlE+lvlErange) ):
            Ef_match = True
        
        if( Ei_match and useEi  ):
            self.__lvls_by_qualifed_gams.append(Ei)
            self.__lvls_by_qualifed_gams.append(Ef)

        if( Ef_match and useEf  ):
            self.__lvls_by_qualifed_gams.append(Ei)
            self.__lvls_by_qualifed_gams.append(Ef)
        
        return ( Ei_match, Ef_match )
        

    def __test_gamE(self, gam, gamE ):
        '''
        check a gamE can match Ei and Ef 
        '''
        # used in self.select_gams_by_gamE()
        gamE = float( gamE )
        Ei = float( gam['Ei'] )
        Ef = float( gam['Ef'] )
        
        gamE_toTest = Ei - Ef
        
        if( gamE_toTest>(gamE-self.gamErange) and\
            gamE_toTest<(gamE+self.gamErange) ):
            self.__lvls_by_qualifed_gams.append(Ei)
            self.__lvls_by_qualifed_gams.append(Ef)
            return True
        else:
            return False
        pass    
    
    def __test_lvl2(self, lvlE, list_lvlE):
        '''
        to see whether lvlE is in list_lvlE, within lvlErange.
        '''
        flag = False
        for E in list_lvlE:
            if( lvlE >= (E-self.lvlErange) and lvlE <= (E+self.lvlErange) ):
                flag = True
        return flag
        pass

    def __test_lvl(self, lvlE1, lvlE2 ):
        """ to see if lvlE1 is with in the range of lvlE2."""
        lvlE1 = float( lvlE1 )
        lvlE2 = float( lvlE2 )
        lvlErange = self.lvlErange
        lvlE_match = False
         
        if( lvlE1 >(lvlE2-lvlErange) and  lvlE1<(lvlE2+lvlErange) ):
            lvlE_match = True
        return lvlE_match
        
    def __test_no_selection(self):
        '''
        if we dont have any lvl or gam selected, just 
        plot the lvls and gams after pre_sort.
        '''
        outStr = ""
        if(  len(self.__lvls_by_qualifed_gams)==0 ): 
            
            for lvl in self.list_lvl:
                lvlE  = lvl['lvlE']
                bandN = lvl['bandN']
                if( 'spin' in lvl): 
                    spin = lvl['spin'];
                    outStr += \
                    "@lvlE %s @bandN %s @spin %s \n" %( lvlE, bandN, spin )
                else:  
                     outStr += \
                    "@lvlE %s @bandN %s \n" %( lvlE, bandN )

            for gam in self.list_gam:
                Ei = gam['Ei']
                Ef = gam['Ef']
                label = float(Ei) - float(Ef)
                label = "%.f" %label 
                # if we have label from gam, just use it original setting.
                if( "label" in gam): label = gam['label']
            
                outStr += "@Ei %s @Ef %s @color blue @I 10 @label %s\n" \
                           %(Ei, Ef, label) 
                pass
            return True, outStr
        else:
            return False, outStr
             
        pass


    def reset(self):
        self.list_gam_new = []
        self.list_lvl_new = []
        self.__lvls_by_qualifed_gams = []
        self.__lvls_highlight = []
        self.__lvls_no_gam = []
        pass
    
    
    def select_gams_by_lvls(self, lvls_input=[],useEi=True, useEf=True):
        """ 
        gam whose Ei and Ef in the lvls_input will be selected 

        gam whose Ei in the lvls_highlight will be selected when useEi = True
        gam whose Ef in the lvls_highlight will be selected when useEf = True
        """
        
        lvls_input = self.__no_duplicate( lvls_input )

        # pasre each gam to see whether Ei or Ef matches the lvls_input
        for gam in self.list_gam:
            
            for lvlE in lvls_input:
               
                (Ei_match, Ef_match) = self.__test_gam( gam, lvlE, useEi, useEf )
                # in the __test_gam, we will also handle
                # __lvls_by_qualifed_gams
                
                 
                if( Ei_match and useEi ):
                    if( gam not in self.list_gam_new ):
                        self.list_gam_new.append( gam )
                if( Ef_match and useEf  ):
                    if( gam not in self.list_gam_new ):
                        self.list_gam_new.append( gam )

        
        # let lvls_input to be appended to lvls_highlight
        for lvlE in lvls_input:
            if( lvlE not in self.__lvls_highlight ):
                self.__lvls_highlight.append( lvlE )
        pass
    
       
    def select_gams_by_gamE(self, gamEs_input = []):
        """ """
        gamEs_input = self.__no_duplicate( gamEs_input ) 
        
        
        for gam in self.list_gam: # gam from our original data.
            
            for gamE in gamEs_input: # gamE from our select energy.
                
                gamE_match = self.__test_gamE( gam, gamE ) 
                
                if( gamE_match ):
                    if( gam  not in self.list_gam_new ):
                        self.list_gam_new.append( gam )
                    pass
            pass
         
    def select_lvls_by_lvlE(self, lvlEs_input = []):
         
        # to check a lvlE_input is within a lvlE+-lvlErange 
        # if true, we append the input to self.__lvls_no_gam
        for lvlE_input in lvlEs_input:
            for lvl in self.list_lvl:
                lvlE = float(lvl['lvlE'])

                if( self.__test_lvl(lvlE_input, lvlE) ):
                    self.__lvls_no_gam.append( lvlE_input )
        
        pass

    def __write_out_and_run(self, outFileName, outStr, use_evince):
        '''
        writ out to file , and run lvl_builder.
        '''
        with open(outFileName,"w") as f: f.write( outStr )

         
        cmd = "./lvl_builder.py %s hl_config.txt hl.agr" %( outFileName)
        subprocess.call( cmd, shell=True)
        
        if( use_evince ):
            cmd = "evince hl.ps &"
            subprocess.call( cmd, shell=True)
            pass
        pass
    
    def show(self, outFileName="hl.txt", use_evince=False):
        
        if( len(self.__lvls_no_gam )>0 ):
            for item in self.__lvls_no_gam:
                self.__lvls_by_qualifed_gams.append( float(item) )
        self.__lvls_by_qualifed_gams = \
        self.__no_duplicate( self.__lvls_by_qualifed_gams ) 
       
        outStr =""
        if( self.__test_no_selection()[0] ):

            # when there is no qualifed lvl.
            # we just plot the lvl and gams after pre_sort.
            print( "no selected lvls or gams, use lvls and gams within enrgy limits." )
            outStr = self.__test_no_selection()[1]
            self.__write_out_and_run( outFileName, outStr, use_evince )
            return;

        
        for lvl1 in self.list_lvl:
            lvlE1 = lvl1['lvlE']
            bandN = lvl1['bandN']

            #-----------------------------------------------------
            # when a lvl is highlighted, add @linewidth 20 to it.
            lineW = ""
            for lvlE2 in self.__lvls_highlight:
                if( self.__test_lvl(lvlE1, lvlE2) and \
                    self.__highlight_lvl ):
                    lineW = "@linewidth 20 "
             


            #-----------------------------------------------------
            # spin info
            if( 'spin' in lvl1): 
                spin = lvl1['spin']
            else: spin = 'NA'
             

            #------------------------------------------------------
            if( self.__force_to_show_all_lvls ):
                # show all states
                outStr += "@lvlE %s @bandN %s @spin %s %s \n" %( lvlE1, bandN, spin, lineW )

            elif( self.__test_lvl2( float(lvlE1), self.__lvls_by_qualifed_gams ) and \
                not self.__force_to_show_all_lvls ):
                # only show partial lvls
                outStr += "@lvlE %s @bandN %s @spin %s %s \n" %( lvlE1, bandN, spin, lineW )
            
                 
                
        for gam in self.list_gam_new:
            Ei = gam['Ei']
            Ef = gam['Ef']
            label = float(Ei) - float(Ef)
            label = "%.f" %label 
            # if we have label from gam, just use it original setting.
            if( "label" in gam): label = gam['label']
            
            outStr += "@Ei %s @Ef %s @color blue @I 10 @label %s\n" \
                           %(Ei, Ef, label) 
         
        # write out and run lvl_builder.
        self.__write_out_and_run( outFileName, outStr, use_evince )
        

class Run():
    '''
    an interface for highligher class.
    '''
    def __init__( self, inFile=""):
        self.__inFile = inFile
        self.__lvls_from = []
        self.__lvls_to   = []
        self.__lvls_both = [] # both decay from and to
        self.__lvls_no_gam = [] # just level no connection gams.
        self.__gamEs     = []

        self.lvlErange = 2.
        self.gamErange = 2.
        self.lvlE_limitL = 0.
        self.lvlE_limitU = 30000. # 30MeV
        
        self.hl = None  # hl is for HighLight-er
        if( self.__is_input_file_OK(inFile)  ):
            self.hl = Highlighter( inFile )

       
        while( 1 ):
            self.__process()
        
        pass

    def __is_input_file_OK(self, inFile ):
        """ to check whether we can open the file or not."""
        try:
            ftest = open( inFile, "r")
            ftest.close()
            return True
        except IOError:
            return False;

    def __change_input_file(self):
        """  to get user input for lvl and gam source """
        while( 1 ):
            inFile = input( "Input File = ")
            try:
                ftest = open( inFile, "r")
                break;
            except IOError:
                print( "%s does not exist. Please input another one." %inFile)
        ftest.close()
        
        self.__inFile = inFile
        self.hl =  Highlighter( inFile )
        
        pass

    def __change_lvlE_limits( self ):
        limits = input( "lower and upper limits (use , to separate) : " )
        self.lvlE_limitL, self.lvlE_limitU = limits.split(",")
        self.lvlE_limitL = float( self.lvlE_limitL )
        self.lvlE_limitU = float( self.lvlE_limitU )
        pass

    def __change_Erange( self ):
        limits = input( "energy range for lvl and gam (use , to separate) : " )
        self.lvlErange, self.gamErange = limits.split(",")
        self.lvlErange = float( self.lvlErange )
        self.gamErange = float( self.gamErange )
        pass

    def __print_add_gamE(self, gamEs ):
        ''' print our selected gamEs '''
        if( len( gamEs ) == 0 ):
            print( "NONE" )
        else:
            gamEs.sort( key= lambda x: x )
            for idx, gamE in zip( range(len(gamEs)), gamEs):
                gamE = float( gamE )
                print( "%4.f" %gamE, end=" " )
                if( (idx+1)%8 == 0 ): print("") # to make 8 elements a row
            print( "\n" )
    
    def __print_gamEs(self):
        '''
        to let user know what are the available gamEs. 
        we don't change self.hl.list_gam here. 
        '''
        print( "All available levels: ")
        gamEs = []
        for gam in self.hl.list_gam:
            Ei = float( gam['Ei'] )
            Ef = float( gam['Ef'] )
            gamE =  Ei-Ef
            if( gamE not in gamEs ): gamEs.append( gamE )
        
        gamEs.sort( key= lambda x: x )
        for idx, gamE in zip( range(len(gamEs) ), gamEs):
            print(  "%4.f" %gamE, end=" " )  
            if( (idx+1)%8 == 0 ): print("")
        print( "\n--------------------------------------------" )
        pass

    def __print_add_lvls(self, lvls ):
        ''' print our selected lvls '''
        if( len( lvls ) == 0 ):
            print( "NONE" )
        else:
            lvls.sort( key= lambda x: x )
            
            for idx, lvlE in zip( range(len(lvls)), lvls):
                lvlE = float(lvlE)
                print( "%4.f" %lvlE, end=" " )
                if( (idx+1)%5 == 0 ): print("") # to make 5 elements a row
            print( "\n" )
        
    def __print_lvls(self):
        '''
        to let user know what are the available levels. 
        we don't change self.hl.list_lvl. 
        '''
        print( "All available levels: ")
        strOuts = []
        for lvl in self.hl.list_lvl:
            lvlE = float( lvl['lvlE'] )
            if( lvlE <= self.lvlE_limitU and lvlE >= self.lvlE_limitL ):
                s = "%.f" %lvlE 
                if( s not in strOuts ): strOuts.append( s )
        
        for idx, s in zip( range(len(strOuts) ), strOuts):
            print(  "%4s" %s, end=" " )  
            if( (idx+1)%5 == 0 ): print("")
        print( "\n--------------------------------------------" )
        pass

    def __add_gam_to_or_from_level( self, decay_to, decay_from ):

        if( self.hl == None ):
            print( "You have NOT set input file for the source of gam and lvl.")
            input( "press any key to continue")
            return

        #--------------------------------------------
        while(1):
            os.system('clear');
            self.__print_lvls() 
            

            if( decay_to and not decay_from ):
                print( "we have gammas decaying to the final levels:")
                self.__print_add_lvls( self.__lvls_to )

            if( decay_from and not decay_to ):
                print( "we have gammas decaying to the inital levels:")
                self.__print_add_lvls( self.__lvls_from )
            
            if( decay_from and decay_to ):
                print( "we have gammas decaying to/from the levels:")
                self.__print_add_lvls( self.__lvls_both )
          
            print("\ninput a number for level energy, or use following options:")
            opt = \
            input( "(a) add levels \n(r) remove levels \n(d) remove ALL \n(X) exit\nYour option:  ")
            if( opt.lower() == "a"  ):
                lvls_tmp = input( "Input level energies (separate spaces): ")
                items = lvls_tmp.split()
                for item in items:
                    item = float(item)

                    if( decay_to and not decay_from ):
                        if( item not in self.__lvls_to \
                            and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                            self.__lvls_to.append( item )

                    if( decay_from and not decay_to ):
                        if( item not in self.__lvls_from \
                            and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                            self.__lvls_from.append( item )
                    
                    if( decay_from and decay_to ):
                        if( item not in self.__lvls_both \
                            and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                            self.__lvls_both.append( item )
            elif( opt.isdigit() ):
                item = float(opt)
                if( decay_to and not decay_from ):
                    if( item not in self.__lvls_to \
                        and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                        self.__lvls_to.append( item )

                if( decay_from and not decay_to ):
                    if( item not in self.__lvls_from \
                        and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                        self.__lvls_from.append( item )
                
                if( decay_from and decay_to ):
                    if( item not in self.__lvls_both \
                        and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                        self.__lvls_both.append( item )

            elif( opt.lower() == "r" ):
                lvls_tmp = input( "Input level energy (separate spaces): ")
                items = lvls_tmp.split()
                for item in items:
                    item = float(item)

                    if( decay_to and not decay_from ):
                        if( item in self.__lvls_to ):
                            self.__lvls_to.remove( item )

                    if( decay_from and not decay_to ):
                        if( item in self.__lvls_from ):
                            self.__lvls_from.remove( item )

                    if( decay_from and decay_to ):
                        if( item in self.__lvls_both ):
                            self.__lvls_both.remove( item)
            
            elif( opt.lower() == "d" ):
                 
                if( decay_to and not decay_from ): self.__lvls_to = []

                if( decay_from and not decay_to ): self.__lvls_from = []

                if( decay_from and decay_to ): self.__lvls_both = []
                
            elif( opt.lower() == "x" ):
                break;

            


 
            
        pass

    def __add_gams_by_gamEs( self ):

        if( self.hl == None ):
            print( "You have NOT set input file for the source of gam and lvl.")
            input( "press any key to continue")
            return

        while(1):
            os.system('clear');
            self.__print_gamEs()
            print( "we have gamE selected:")
            self.__print_add_gamE( self.__gamEs )
             

            print("\ninput a number for gam energy, or use following options:")
            opt = \
            input( "(a) add gamEs \n(r) remove gamEs \n(d) remove ALL\n(X) exit\nYour option:  ")
            if( opt.lower() == "a" ):
                gamEs_tmp = input( "Input gam energies (separate spaces): ")
                items = gamEs_tmp.split()
                for item in items:
                    item = float(item)
                    if( item not in self.__gamEs ):
                        self.__gamEs.append( item )
            elif( opt.isdigit() ):
                item = float( opt )
                if( item not in self.__gamEs ):
                        self.__gamEs.append( item )

            elif( opt.lower() == "r" ):
                lvls_tmp = input( "Input gam energies (separate spaces): ")
                items = lvls_tmp.split()
                for item in items:
                    item = float(item)
                    if( item in self.__gamEs ):
                        self.__gamEs.remove( item)
            elif( opt.lower() == "d" ):
                self.__gamEs = []

            elif( opt.lower() == "x" ):
                break;

    def __add_lvls_by_lvlEs( self ):
        
        if( self.hl == None ):
            print( "You have NOT set input file for the source of gam and lvl.")
            input( "press any key to continue")
            return

        while(1):
            os.system('clear');
            self.__print_lvls()
            print( "selected levels (no gam):") 
            self.__print_add_lvls( self.__lvls_no_gam )

            print("\ninput a number for level energy ( level will be added but no gmas),\nor use following options:")
            opt = \
            input( "(a) add levels \n(r) remove levels \n(d) remove ALL \n(X) exit\nYour option:  ")
            
            if( opt.lower() == "a"  ):
                lvls_tmp = input( "Input level energies (separate spaces): ")
                items = lvls_tmp.split()
                for item in items:
                    item = float(item)
                    if( item not in self.__lvls_no_gam \
                        and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                        self.__lvls_no_gam.append( item )
 
            elif( opt.isdigit() ):
                item = float(opt)               
                if( item not in self.__lvls_no_gam \
                    and item <= self.lvlE_limitU and item>=self.lvlE_limitL ):
                    self.__lvls_no_gam.append( item )
 

            elif( opt.lower() == "r" ):
                lvls_tmp = input( "Input level energy (separate spaces): ")
                items = lvls_tmp.split()
                for item in items:
                    item = float(item)
                    if( item in self.__lvls_no_gam ):
                        self.__lvls_no_gam.remove( item )
             
            elif( opt.lower() == "d" ):
                 
                self.__lvls_no_gam = []
                
            elif( opt.lower() == "x" ):
                break;



        pass

    def __show(self):
        if( self.hl == None ):
            print( "You have NOT set input file for the source of gam and lvl.")
            input( "press any key to continue")
            return
        self.hl.reset()
        
        # presort
        self.hl.set_lvlE_limit( self.lvlE_limitU, self.lvlE_limitL )
        self.hl.pre_sort()

        # the range setting.
        self.hl.set_lvlErange( self.lvlErange )
        self.hl.set_gamErange( self.gamErange )

        # selection by lvls
        self.hl.select_gams_by_lvls( self.__lvls_to, False, True)
        self.hl.select_gams_by_lvls( self.__lvls_from, True, False)
        self.hl.select_gams_by_lvls( self.__lvls_both, True, True)
        # slection by gamE
        self.hl.select_gams_by_gamE( self.__gamEs )

        # selection by lvlE but no gam
        self.hl.select_lvls_by_lvlE( self.__lvls_no_gam )

        self.hl.show( use_evince=True)
        pass

    def __reset( self ):
        if( self.hl == None ):
            print( "You have NOT set input file for the source of gam and lvl.")
            input( "press any key to continue")
            return
        self.__lvls_to   = []
        self.__lvls_from = []
        self.__lvls_both = []
        self.__lvls_no_gam = []
        self.__gamEs     = []
        self.hl.reset()

    def __process( self ):
        '''
        it will be use in the while loop at the __init__, served as 
        the main function to interact with a user.
        '''
        opt = self.__print_menu()
        if( opt.lower() == "a1" ):
            self.__change_input_file()

        elif( opt.lower() == "a2" ):
            self.__change_lvlE_limits()

        elif( opt.lower() == "a3" ):
            self.__change_Erange()
            
        elif( opt == "1" ):
            self.__add_gam_to_or_from_level( 1, 0)
                 
        elif( opt == "2" ):
            self.__add_gam_to_or_from_level( 0, 1)
             
        elif( opt == "3" ):
            self.__add_gam_to_or_from_level( 1, 1)

        elif( opt.lower() == "4" ):
            self.__add_gams_by_gamEs()

        elif( opt.lower() == "5" ):
            self.__add_lvls_by_lvlEs()
             
        elif( opt.lower() == "s" ):
            self.__show()
            input( "press any key to continue")

        elif( opt.lower() == "r" ):
            self.__reset()

        elif( opt.lower() == "xx" ):
            sys.exit(1)


    def __print_menu( self ):
        '''
        print the menu and then return the option.
        '''
        os.system('clear');
        s=""
        strOut =""
        if( self.__inFile == "" ): 
            s = "None"
        else: 
            s = self.__inFile
        strOut += "\n     ~Welcome to level scheme highlighter~  \n"
        strOut += "\n    (a1) set Input file. [current: %s]\n" %s
        
        strOut+="    (a2) set eng limits for levels. [current %.f:%.f] (keV)\n" \
                %(self.lvlE_limitL, self.lvlE_limitU)
        
        strOut+="    (a3) set eng errors for lvl and gam. [current%4.1f:%4.1f]" \
                %(self.lvlErange, self.gamErange)
        strOut+="""
    -----------------------------------------------------------
    (1) add gammas decay to      final   levels at X (keV)
    (2) add gammas decay from    initial levels at X (keV)
    (3) add gammas decay to/from levels at X (keV)
    (4) add gammas via gamma energy (keV)
    (5) add levels via level energy but no gams 
    -----------------------------------------------------------
    (S)  show 
    (R)  reset 
    (XX) Exit  

    Your choice:  """ 
         
        opt = input( strOut )
        return opt.lower()
        
         
    pass     

if __name__ == '__main__':
    '''
    Here are the demos for how to use Highlighter class.
    Author: Pei-Luan Tai
    Date  : June 02, 2018.

    Python version >= 3
    Files : highligher.py, hl_config.txt
    Required: lvl_builder.py
    Output: hl.agr, hl.ps
    '''
     

    if( 1 ):
        inFile = ""
        if( len(sys.argv) == 2 ): inFile = sys.argv[1]
        run = Run( inFile )

    if( 0 ):
        # the following is alternative way to use highligher.
        highligher = Highlighter( "junk.txt")

        # presort
        highligher.set_lvlE_limit( 8000, 0);
        highligher.pre_sort()
    
        # the range setting.
        highligher.set_lvlErange( 2 )
        highligher.set_gamErange( 2 )

        # adding gams decaying from 1695 keV state
        lvls = [ 1695 ]
        highligher.select_gams_by_lvls( lvls, 1, 0 )
        
        # adding gams decaying to 2317 keV state
        lvls = [ 847 ]
        highligher.select_gams_by_lvls( lvls, 0, 1 )
        
        # adding gams with gamE = 1439 +- range
        gamEs = [ 847, 667]
        highligher.select_gams_by_gamE( gamEs )

        # adding lvls but no gam
        lvls = [ 2000 ]
        highligher.select_lvls_by_lvlE( lvls )

        # fine tuning display
        # highligher.set_lvl_highlight( True )
        # highligher.set_force_to_show_all_lvls( False )
        
        highligher.show( use_evince = True )

    
     
     
 
    
    pass
 
    