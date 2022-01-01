#!/usr/bin/python3.4
#note python3 only
import readline  
import xml.dom.minidom
from  xml.dom.minidom import parse, parseString
import urllib.request 
import subprocess
import highlighter
import re
import os
import sys 
import pdb
from NNDC_Parser import NNDCParser
 
   
    
class Run():
    '''
    an interface for NNDCParser.
    '''
    def __init__( self, inFile=""):
         

        # upper energy limit.
        self.lvlE_limitU = 3000 # -1 = no limit

        self.__A_min =  1
        self.__A_max = -1  # -1 = no limit
        self.__A_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__Z_min =  1
        self.__Z_max = -1  # -1 = no limit
        self.__Z_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__N_min =  0
        self.__N_max = -1  # -1 = no limit
        self.__N_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__As = []  # manual selected A
        self.__Zs = []  # manual selected Z
        self.__Ns = []  # manual selected N

        
        self.use_lvl_builder = True
        self.show_gam = True

        self.__valid_syms  = [] # updated at __load_mass16_table
        self.__nuclei_syms = []

        # to use mass16.xml as our symbol table.
        # self.__nuclei_table has a structure of [ (), (), (), ]
        # each elment is ( sym, A, Z, N ) 
        self.__nuclei_table = self.__load_mass16_table()
        self.nuclei_list = self.__nuclei_table[:]
     
        # reaction energy table, for Sn, Sp ...
        # each element is a dic, key = sym, Sn, Sp, S2n, S2p, Qa
        self.__rec_eng_table = self.__load_mass16_Sn_table()   
     
        self.__useRange = True
        
        self.parser = NNDCParser()

        while( 1 ):
            self.__process()
    

    def __load_mass16_table( self ):
        '''
        we load mass16.xml as our symbol table.
        '''
        try:
            f = open("mass16.xml","r")
            f.close()
        except:
            print( "Error: cannot open mass16.xml ")
            print( "Please check the file.")
            sys.exit(0)

        doc = parse( open("mass16.xml") )
        nuclei_table = doc.getElementsByTagName("nuclei")

        nuclei_table_new = []
        for nuclei in nuclei_table:
            sym = nuclei.getAttribute('sym')
            A   = nuclei.getAttribute('A')
            Z   = nuclei.getAttribute('Z')

            A = int(A)
            Z = int(Z)
            N = A-Z
            nuclei_table_new.append( (sym, A, Z, N) )  
            self.__valid_syms.append( sym )


        return nuclei_table_new
 

    def __load_mass16_Sn_table( self ):
        '''
        we load mass16_Sn.xml as our reaction energy table.
        '''
        try:
            f = open("mass16_Sn.xml","r")
            f.close()
        except:
            print( "Error: cannot open mass16_Sn.xml ")
            print( "Please check the file.")
            sys.exit(0)

        doc = parse( open("mass16_Sn.xml") )
        eng_table = doc.getElementsByTagName("nuclei")

        eng_table_new = []
        for nuclei in eng_table:
            sym = nuclei.getAttribute('sym')
            Sn   = nuclei.getAttribute('Sn')
            Sp   = nuclei.getAttribute('Sp')
            S2n  = nuclei.getAttribute('S2n')
            S2p  = nuclei.getAttribute('S2p')
            Qa   = nuclei.getAttribute('Qa')

            try:
                # print ( "debug", Sn,"." )
                Sn = float(Sn)
            except:
                Sn = "None"

            try:
                Sp = float(Sp)
            except:
                Sp = "None"


            try:
                S2n = float(S2n)
            except:
                S2n = "None"


            try:
                S2p = float(S2p)
            except:
                S2p = "None"


            try:
                Qa = float(Qa)
                Sa = -Qa
            except:
                Sa = "None"
            
            tmp_dic = { 'sym': sym,\
                        'Sn' : Sn , 'Sp' : Sp,\
                        'S2n': S2n, 'S2p': S2p,\
                        'Sa' : Sa }
            eng_table_new.append( tmp_dic )  
        
        return eng_table_new
    

    def __get_eng_limits( self, sym_input, \
        lowE_type, lowE_shift, uppE_type, uppE_shift ):
        '''
        lowE_type and uppE_type are keys.
        when we can found key 'Sn', 'Sp' ... in a nuclei
        then we return good_status = True.
        note: some nuclei don't have Sn value from table.
        '''
        good_status = True
        if( lowE_type == "gs" ): E1 = 0.
        if( uppE_type == "gs" ): E2 = 0.

        for tmp_dic in self.__rec_eng_table:
            sym = tmp_dic['sym']

            if( sym == sym_input ):
                if( lowE_type in tmp_dic ):
                    E1 = tmp_dic[lowE_type]
                    if( E1 == "None" ): good_status = False
                if( uppE_type in tmp_dic ):
                    E2 = tmp_dic[uppE_type]
                    if( E2 == "None" ): good_status = False
        
        if( good_status ):            
            E1 += lowE_shift
            E2 += uppE_shift
        else: 
            E1 = E2= 0
        
       

        return E1, E2, good_status 
        pass



    def __print_selected_nuclei( self ):
        '''
        (1) print out the selected nuclei_list
        (2) update self.nuclei_list
        '''
        nuclei_list = []

        # -----------manual selection -----------
        # if when using manual selection, the range selection
        # will be skip.

         

        if len( self.__As ) > 0 :
            for nuclei in self.__nuclei_table:
                A = nuclei[1]
                if A in self.__As:  
                    nuclei_list.append( nuclei )
        else:
            nuclei_list = self.__nuclei_table[:] 
        # print( "debug 1, len = ", len(nuclei_list) ) 


        tmp_list = []
        if len( self.__Zs ) > 0 :   
            for nuclei in nuclei_list:
                Z = nuclei[2]
                if Z in self.__Zs:  
                    tmp_list.append( nuclei )
            nuclei_list = tmp_list[:]
        # print( "debug 2, len = ", len(nuclei_list) ) 


        tmp_list = []
        if len( self.__Ns ) > 0 :   
            for nuclei in nuclei_list:
                N = nuclei[3]
                if N in self.__Ns:  
                    tmp_list.append( nuclei )
            nuclei_list = tmp_list[:]
        # print( "debug 3, len = ", len(nuclei_list) )  



        # -----------range  selection -----------
        # do A selection
        tmp_list = []
        if( self.__A_max == -1  ):
            # no limit, so we add in all nuclei.
            for nuclei in nuclei_list:
                tmp_list.append( nuclei )
        elif( self.__A_max >= 1  ):
            for nuclei in nuclei_list:
                A = nuclei[1]
                if( A >= self.__A_min and A <= self.__A_max ):
                    tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]

        # deal with odd/even A
        tmp_list = []
        for nuclei in nuclei_list:
            A = nuclei[1]
            Odd_A  = False
            Even_A = False
            if( A % 2 == 1 ): Odd_A  = True
            if( A % 2 == 0 ): Even_A = True
            if(   self.__A_flag == 1 and Odd_A ):
                tmp_list.append( nuclei )
            elif( self.__A_flag == 2 and Even_A ):
                tmp_list.append( nuclei )
            elif(  self.__A_flag == 0 ):
                tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]


        # do Z selection
        tmp_list = []
        if( self.__Z_max == -1  ):
            # no limit, so we add in all nuclei.
            for nuclei in nuclei_list:
                tmp_list.append( nuclei )
        elif( self.__Z_max >= 1  ):
            for nuclei in nuclei_list:
                Z = nuclei[2]
                if( Z >= self.__Z_min and Z <= self.__Z_max ):
                    tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]

        # deal with odd/even Z
        tmp_list = []
        for nuclei in nuclei_list:
            Z = nuclei[2]
            Odd_Z  = False
            Even_Z = False
            if( Z % 2 == 1 ): Odd_Z  = True
            if( Z % 2 == 0 ): Even_Z = True
            if(   self.__Z_flag == 1 and Odd_Z ):
                tmp_list.append( nuclei )
            elif( self.__Z_flag == 2 and Even_Z ):
                tmp_list.append( nuclei )
            elif(  self.__Z_flag == 0 ):
                tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]




        # do N selection
        tmp_list = []
        if( self.__N_max == -1  ):
            # no limit, so we add in all nuclei.
            for nuclei in nuclei_list:
                tmp_list.append( nuclei )
        elif( self.__N_max >= 1  ):
            for nuclei in nuclei_list:
                N = nuclei[3]
                if( N >= self.__N_min and N <= self.__N_max ):
                    tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]

        # deal with odd/even Z
        tmp_list = []
        for nuclei in nuclei_list:
            N = nuclei[3]
            Odd_N  = False
            Even_N = False
            if( N % 2 == 1 ): Odd_N  = True
            if( N % 2 == 0 ): Even_N = True
            if(   self.__N_flag == 1 and Odd_N ):
                tmp_list.append( nuclei )
            elif( self.__N_flag == 2 and Even_N ):
                tmp_list.append( nuclei )
            elif(  self.__N_flag == 0 ):
                tmp_list.append( nuclei )
        nuclei_list = tmp_list[:]

        # update 
        self.nuclei_list = nuclei_list[:]

        # output sting
        outStr = "\n    %4d nuclei are selected:\n    "\
             %len( nuclei_list)
        
        

        if len( nuclei_list) > 10:
            # over than 10 items

             
            # first 5
            for nuclei in nuclei_list[:5]:
                sym = nuclei[0]
                outStr += "%5s " %sym
            outStr += "...\n    "

            # last 5
            tmp_list = []
            for i in range(5):
                idx =  -1*i - 1
                nuclei = nuclei_list[ idx ]
                sym = nuclei[0]
                tmp_list.append( sym)
            
            for x in reversed( tmp_list):
                outStr += "%5s " %x
        else:
            # less or equal to 10 items.
            itemp = 0
            for nuclei in nuclei_list[:10]:
                sym = nuclei[0]
                outStr += "%5s " %sym
                itemp  += 1
                if itemp == 5: outStr += "\n    "


        #=========================================
        # for manual input
        if( not self.__useRange ):
            outStr2 =  "\n    %4d nuclei are selected:\n    "\
             %len(self.__nuclei_syms)
            
            if len(self.__nuclei_syms) > 10:
                #first 5
                for sym in self.__nuclei_syms:
                    outStr2 += "%5s " %sym
                    outStr2 += "...\n    "
                #last 5
                for i in range(5):
                    idx =  -1*i - 1
                    sym = self.__nuclei_syms[idx]
                    outStr2 += "%5s " %sym
            else:
                # less or equal to 10 items.
                itemp = 0
                for sym in self.__nuclei_syms[:10]:
                
                    outStr2 += "%5s " %sym
                    itemp  += 1
                    if itemp == 5: outStr2 += "\n    "
            return outStr2 


        return outStr 
        pass

    def __set_A_flag( self ):
        opt = input( "Set A to (0) none, (1) odd, (2) even :" )
        opt = opt.rstrip()
        opt = opt.lstrip()

        if opt == "0" :
            self.__A_flag = 0
        elif opt == "1" :
            self.__A_flag = 1
        elif opt == "2" :
            self.__A_flag = 2
        else:
            self.__A_flag = 0

    def __set_Z_flag( self ):
        opt = input( "Set Z to (0) none, (1) odd, (2) even :" )
        opt = opt.rstrip()
        opt = opt.lstrip()

        if opt == "0" :
            self.__Z_flag = 0
        elif opt == "1" :
            self.__Z_flag = 1
        elif opt == "2" :
            self.__Z_flag = 2
        else:
            self.__Z_flag = 0

    def __set_N_flag( self ):
        opt = input( "Set N to (0) none, (1) odd, (2) even :" )
        opt = opt.rstrip()
        opt = opt.lstrip()

        if opt == "0" :
            self.__N_flag = 0
        elif opt == "1" :
            self.__N_flag = 1
        elif opt == "2" :
            self.__N_flag = 2
        else:
            self.__N_flag = 0


    def __set_As( self ):
        As = input( "input numbers (separate by spaces): ")
        As = As.split()
        for item in As:
            item = int( item )
            self.__As.append( item )
        
        # force to skip range selection.
        if( len( self.__As ) > 0 ):
            self.__A_max = -1  # -1 = no limit

        pass

    def __set_Zs( self ):
        Zs = input( "input numbers (separate by spaces): ")
        Zs = Zs.split()
        for item in Zs:
            item = int( item )
            self.__Zs.append( item )
        
        # force to skip range selection.
        if( len( self.__Zs ) > 0 ):
            self.__Z_max = -1  # -1 = no limit

        pass

    def __set_Ns( self ):
        Ns = input( "input numbers (separate by spaces): ")
        Ns = Ns.split()
        for item in Ns:
            item = int( item )
            self.__Ns.append( item )
        
        # force to skip range selection.
        if( len( self.__Ns ) > 0 ):
            self.__N_max = -1  # -1 = no limit

        pass



    def __set_A_selection( self ):
        
        while( 1 ):
            os.system('clear');
            print( "    ->SELECTION SUMMARY->A SELECTION SUBMENU")
            print( self.__print_status() )
            print( self.__print_selected_nuclei() )
            print("    --------------------------------\n")
           
             
            print( "    (a) add one or more" )
            print( "    (s) set odd/even " )
            print( "    (R) Reset A selections")
            print( "    (X) Done")
            print( "    Or input two num for A1 and A2 range (separate by spaces) ")
            opt = input( "\nYour choice: " )
            
            if   opt.lower() == "x": break

            elif opt.lower() == "a": self.__set_As()

            elif opt.lower() == "s": self.__set_A_flag()

            elif opt.lower() == "r" :
                self.__A_min =  1
                self.__A_max = -1  # -1 = no limit
                self.__A_flag = 0  #  0 = none, 1 = odd, 2 = even
                self.__As = []
            
             
            opt = opt.split()
            if len(opt) == 2:
                As = [ int(opt[0]), int(opt[1]) ] 
                self.__A_min = min( As )
                self.__A_max = max( As )    
            if  self.__A_min < 1 : self.__A_min = 1


    def __set_Z_selection( self ):
        
        while( 1 ):
            os.system('clear');
            print( "    ->SELECTION SUMMARY->Z SELECTION SUBMENU")
            print( self.__print_status() )
            print( self.__print_selected_nuclei() )
            print("    --------------------------------\n")
           
             
            print( "    (a) add one or more" )
            print( "    (s) set odd/even " )
            print( "    (R) Reset Z selections")
            print( "    (X) Done")
            print( "    Or input two num for Z1 and Z2 range (separate by spaces) ")
            opt = input( "\nYour choice: " )
            
            if   opt.lower() == "x": break

            elif opt.lower() == "a": self.__set_Zs()

            elif opt.lower() == "s": self.__set_Z_flag()

            elif opt.lower() == "r" :
                self.__Z_min =  1
                self.__Z_max = -1  # -1 = no limit
                self.__Z_flag = 0  #  0 = none, 1 = odd, 2 = even
                self.__Zs = []
            
             
            opt = opt.split()
            if len(opt) == 2:
                Zs = [ int(opt[0]), int(opt[1]) ] 
                self.__Z_min = min( Zs )
                self.__Z_max = max( Zs )    
            if  self.__Z_min < 1 : self.__Z_min = 1


    def __set_N_selection( self ):
        
        while( 1 ):
            os.system('clear');
            print( "    ->SELECTION SUMMARY->N SELECTION SUBMENU")
            print( self.__print_status() )
            print( self.__print_selected_nuclei() )
            print("    --------------------------------\n")
           
             
            print( "    (a) add one or more" )
            print( "    (s) set odd/even " )
            print( "    (R) Reset N selections")
            print( "    (X) Done")
            print( "    Or input two num for N1 and N2 range (separate by spaces) ")
            opt = input( "\nYour choice: " )
            
            if   opt.lower() == "x": break

            elif opt.lower() == "a": self.__set_Ns()

            elif opt.lower() == "s": self.__set_N_flag()

            elif opt.lower() == "r" :
                self.__N_min =  1
                self.__N_max = -1  # -1 = no limit
                self.__N_flag = 0  #  0 = none, 1 = odd, 2 = even
                self.__Ns = []
            
             
            opt = opt.split()
            if len(opt) == 2:
                Ns = [ int(opt[0]), int(opt[1]) ] 
                self.__N_min = min( Ns )
                self.__N_max = max( Ns )    
            if  self.__N_min < 1 : self.__N_min = 1






    def __reset_nuclei_selection( self ):
        self.__A_min =  1
        self.__A_max = -1
        self.__A_flag = 0

        self.__Z_min =  1
        self.__Z_max = -1
        self.__Z_flag = 0

        self.__N_min =  0
        self.__N_max = -1
        self.__N_flag = 0

        self.__nuclei_syms = []
        pass

    def __print_A_status( self ):
        
        # range selection part
        if self.__A_max < 1:
            sA_selection = "None"
        if self.__A_max >= 1:
            sA_selection = "%3d:%3d" %(self.__A_min, self.__A_max)

        if self.__A_flag == 1: sA_selection += " odd A"
        if self.__A_flag == 2: sA_selection += " even A"
        sA_selection = "    A1 <= A <= A2 [current %s]"%(sA_selection)

        # manual selection part
        if len(self.__As) > 0:
            sA_selection = "    A = ["
            for item in self.__As:
                sA_selection += "%2d, " %item
            
            # remove the last ", "
            sA_selection = sA_selection[:-2]
            sA_selection += " ]"

        return sA_selection
         
    def __print_Z_status( self ):
        
        # range selection part
        if self.__Z_max < 1:
            sZ_selection = "None"
        if self.__Z_max >= 1:
            sZ_selection = "%3d:%3d" %(self.__Z_min, self.__Z_max)
        
        if self.__Z_flag == 1: sZ_selection += " odd Z"
        if self.__Z_flag == 2: sZ_selection += " even Z"
        sZ_selection = "    Z1 <= Z <= Z2 [current %s]"%(sZ_selection)
        
        # manual selection part
        if len(self.__Zs) > 0:
            sZ_selection = "    Z = ["
            for item in self.__Zs:
                sZ_selection += "%2d, " %item
            
            # remove the last ", "
            sZ_selection = sZ_selection[:-2]
            sZ_selection += " ]"

        return sZ_selection

    def __print_N_status( self ):

        # range selection part
        if self.__N_max < 1:
            sN_selection = "None"
        if self.__N_max >= 1:
            sN_selection = "%3d:%3d" %(self.__N_min, self.__N_max)
        
        if self.__N_flag == 1: sN_selection += " odd N"
        if self.__N_flag == 2: sN_selection += " even N"
        sN_selection = "    N1 <= N <= N2 [current %s]"%(sN_selection)

        # manual selection part
        if len(self.__Ns) > 0:
            sN_selection = "    N = ["
            for item in self.__Ns:
                sN_selection += "%2d, " %item
            
            # remove the last ", "
            sN_selection = sN_selection[:-2]
            sN_selection += " ]"

        return sN_selection

    def __print_status( self ):
        strOut = ""
        strOut += self.__print_A_status() + "\n"
        strOut += self.__print_Z_status() + "\n"
        strOut += self.__print_N_status() 
        
        return strOut

    def __print_select_nuclei_menu( self ):
        
        strOut = "    ->SELECTION SUMMARY\n" 
        strOut += self.__print_status() + "\n"
        strOut += self.__print_selected_nuclei() + "\n"
        strOut += "    --------------------------------\n\n"
        
        strOut += "    (1) select A or set (A1,A2) range\n" 
        strOut += "    (2) select Z or set (Z1,Z2) range\n" 
        strOut += "    (3) select N or set (N1,N2) range\n" 
        strOut += "     \n"
        strOut += "    (4) select nuclei symbols  \n" 
        strOut += "    --------------------------------\n"
        strOut += "    (R) Reset selections \n"
        strOut += "    (X) Done \n"
        print( strOut )
        opt = input("Your choice: ")
        
        return opt
        
        pass

    
    def __set_sym_selection( self ):
        
        print( "Input symbols ex. 4He 7Li (separate by spaces), and 0 for reset. ")
        # print( "Only valid symbols will be added.")
        opt = input( "Your choice:  "  )

        if opt == "0":
            self.__nuclei_syms = []
        else:
            syms = opt.split()
            for sym in syms:
                if sym in self.__valid_syms:
                    self.__nuclei_syms.append( sym )
        pass

    def __select_nuclei( self ):
        
        while( 1 ):
            os.system('clear');
            opt = self.__print_select_nuclei_menu()

            if opt == "1" :
                self.__useRange = True
                self.__nuclei_syms = [] # reset
                self.__set_A_selection()
            
            elif opt == "2" :
                self.__useRange = True
                self.__nuclei_syms = [] # reset
                self.__set_Z_selection()

            elif opt == "3" :
                self.__useRange = True
                self.__nuclei_syms = [] # reset
                self.__set_N_selection()

            elif opt == "4":
                # disable selection by range.
                # we do manual input.
                self.__useRange = False

                # we set the range selection
                self.__A_min =  1
                self.__A_max = -1
                self.__A_flag = 0

                self.__Z_min =  1
                self.__Z_max = -1
                self.__Z_flag = 0

                self.__N_min =  0
                self.__N_max = -1
                self.__N_flag = 0

                self.__set_sym_selection()

            elif opt.lower() == 'r' :
                # to reset ALL
                self.__reset_nuclei_selection()

            elif opt.lower() == 'x' :
                break

        
        pass

    def __set_upper_energy_limit( self ):
        limit = input( "input the upper energy limits in keV (0=none): " )

         
        try:
            fLimit = float( limit )
            self.lvlE_limitU = fLimit
        except:
            self.lvlE_limitU = -1

        if limit == "0" : self.lvlE_limitU = -1


        pass

    def __set_use_lvl_builder( self ):

        opt = input( "to use lvl_builder? (y/N): " )
        if opt.lower() == "n" or len(opt)==0: self.use_lvl_builder = False
        elif opt.lower() == 'y': self.use_lvl_builder = True
        else: self.use_lvl_builder = False

    def __set_show_gam( self ):

        opt = input( "to show gammas? (y/N): " )
        if opt.lower() == "n" or len(opt)==0:  self.show_gam = False
        elif opt.lower() == 'y':  self.show_gam = True
        else: self.show_gam = False

    def __process( self ):
        '''
        it will be use in the while loop at the __init__, served as 
        the main function to interact with a user.
        '''
        opt = self.__print_main_menu() 
        # opt = "a1"
        # self.__nuclei_syms = ["31Si", ]

        if( opt.lower() == "1" ):
            self.__select_nuclei()

        elif( opt.lower() == "2" ):
            self.__set_upper_energy_limit()

        elif( opt.lower() == "3" ):
            self.__set_use_lvl_builder()

        elif( opt.lower() == "4" ):
            self.__set_show_gam()

        elif( opt.lower() == "a1" ):
            os.system('clear')
            self.__run_plot_lvl_schemes()

        elif( opt.lower() == "a2" ):
            os.system('clear')
            self.__run_find_reference()

        elif( opt.lower() == "a3" ):
            os.system('clear')
            self.__run_plot_lvl_schemes_with_JPIs()

        elif( opt.lower() == "a4" ):
            os.system('clear')
            self.__run_plot_lvl_schemes_with_stateN()

        elif( opt.lower() == "a5" ):
            os.system('clear')
            self.__run_plot_lvl_schemes_with_rec_eng()

        elif( opt.lower() == "r" ):
            self.__reset_to_default()

        elif( opt.lower() == "xx" ):
            sys.exit(1)
    
    def __print_main_menu( self ):
        '''
        print the main menu and then return the option.
        '''
        os.system('clear');
         
        sNucleiList=""
        if( self.__useRange ):
            # selection by range
            if len(self.nuclei_list)== 0  :
                sNucleiList = "None"
            else: 
                sNucleiList = "%2d nuclei" %len(self.nuclei_list)
        else:
            if len(self.__nuclei_syms)== 0  :
                sNucleiList = "None"
            elif len(self.__nuclei_syms) > 5 :
                # over 5 terms
                for sym in self.__nuclei_syms[:5] :
                    sNucleiList += "%s " %sym
                    sNucleiList += "..."
            else:
                for sym in self.__nuclei_syms :
                    sNucleiList += "%s " %sym

        # energy upper limit.
        if self.lvlE_limitU == -1:
            sLvlE_limitU = "None"
        elif self.lvlE_limitU > 0:
            sLvlE_limitU = "%.f" %float( self.lvlE_limitU )

        # use lvl_builder
        if self.use_lvl_builder:
            sUseLvlBuilder = "True"
        else:
            sUseLvlBuilder = "False"

        # show gam
        if self.show_gam:
            sShow_gam = "True"
        else:
            sShow_gam = "False"

        strOut  = "\n     ~Welcome to NNDC parser~  \n"
        strOut += "\n    (1) Select nuclei [current: %s]\n" %sNucleiList  
        strOut+="    (2) upper engergy limit [current: %5s] (keV)\n"%(sLvlE_limitU)
        strOut+="    (3) to use  lvl_builder [current: %5s]\n" %(sUseLvlBuilder)
        strOut+="    (4) to show gammas      [current: %5s]" %(sShow_gam)
        strOut+="""
    -----------------------------------------------------------
    (a1) plot level schemes 
    (a2) plot level schemes with ref selections.
    (a3) plot level schemes with JPi selections
    (a4) plot level schemes with # of states limt
    (a5) plot level schemes with Sn, Sp...limts
    -----------------------------------------------------------
    (R)  Reset to default 
    (XX) Exit  

    Your choice:  """ 
         
        opt = input( strOut )
        return opt.lower()
        
    def __reset_to_default( self ):
        '''
        reset ALL setting.
        '''
        self.lvlE_limitU = 3000 # -1 = no limit

        self.__A_min =  1
        self.__A_max = -1  # -1 = no limit
        self.__A_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__Z_min =  1
        self.__Z_max = -1  # -1 = no limit
        self.__Z_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__N_min =  0
        self.__N_max = -1  # -1 = no limit
        self.__N_flag = 0  #  0 = none, 1 = odd, 2 = even

        self.__As = []  # manual selected A
        self.__Zs = []  # manual selected Z
        self.__Ns = []  # manual selected N

        
        self.use_lvl_builder = True
        self.show_gam = True

        self.__nuclei_syms = []
        self.__useRange = True
        pass

    def __get_symbols( self ):
        '''
        organize our selection to a list of symbols for our 
        selected nuclei.
        '''
        if len(self.__nuclei_syms) > 0 :
            return self.__nuclei_syms
        elif len(self.nuclei_list) > 0:
            nuclei_list = []
            for nuclei in self.nuclei_list:
                sym = nuclei[0]
                nuclei_list.append( sym )
            return nuclei_list[:] 
        else:
            return []

    def __check_has_data( self, nucleus ):
        '''
        to check whether we have data or not for a given nucleus at NNDC
        '''
        # old link
        # url=\
        # 'https://www.nndc.bnl.gov/nudat2/getdataset.jsp?nucleus=%s&unc=nds' %nucleus
        
        url=\
        'https://www.nndc.bnl.gov/nudat3/getdatasetClassic.jsp?nucleus=%s&unc=nds'%nucleus
        
        marker = "<TABLE cellspacing=1 cellpadding=4 width=800>" 
        
        content =""
        with urllib.request.urlopen( url ) as f:
            content = f.read().decode('utf-8')
        if( content.find("Empty dataset") != -1 or \
                content.find(marker) == -1  ): 
            return (False, "")
        else:
            return (True, content )
    
    def __check_JPI( self, cnt_JPIs, JPINs ):
        flag = False

        # ie . (cnt_JP1 < JP1N or cnt_JPI2 < JPI2N) )
        # any one of the condition meets, the flag will be True.
        for i in range( len( JPINs ) ):
            if( cnt_JPIs[i] < JPINs[i] ): 
                flag = True
        return flag

    def __check_ref( self, state_ref, select_list_ref ):
        flag = False


        # if our select list of ref has an element in state refs
        # then return true.
        for x in select_list_ref:
            x = x.rstrip();
            x = x.lstrip()
            if x in state_ref:
                flag = True
        return flag

    def __write_out_results_and_use_lvl_builder( self, outStr, outStr2 ):
        
        with open("nndc_result.txt","w")   as f: f.write( outStr )
        
        if( self.use_lvl_builder ):
            with open("bandText_file.txt","w") as f: f.write( outStr2 )
            cmd = "./lvl_builder.py nndc_result.txt ./demos/NNDC_config.txt \
                output.agr bandText_file.txt"  
            subprocess.call( cmd, shell=True)
        
        input("press any key to continue..")


    def __convert_to_lvl( self, levels, lowerLimt, upperLimt, \
        idx=0, nuclei_N=1, forceNoGam=False ):
        '''
        levels is the object from parser.get_levels()
        upperlimt is an float number  
        idx is used for the band location. 
        
        For just one nuclei( nuclei_N =1 ), idx doesn't matter.
        '''

        outStr = ""
        self.levelN_output = 0

        # control the bandN
        if( nuclei_N == 1 ): 
            # for one nuclei case.
            bandN = "0_5" 
        else: 
            bandN = "%d" %idx

        
        for level in levels:
        
            if( 'Ex' in level and \
                level['Ex'] <= upperLimt and \
                level['Ex'] >= lowerLimt ):
             
                if( 'spin' not in level or level['spin'] == "" ):
                     s = "@lvlE %7.3f%02d @bandN %s @color black  "\
                     %(level['Ex'], idx, bandN )
                else:
                    s = "@lvlE %7.3f%02d @bandN %s @color black @spin %s "\
                    %(level['Ex'], idx, bandN, level['spin'] )
            
                
                outStr += s
                outStr += "\n"
                self.levelN_output += 1

                if( forceNoGam ): continue

                if( not self.show_gam  ): 
                    s = ("#" + "="*78)
                    outStr += s + "\n"
                    continue
                
                if( ('final_states' in level) and len(level['final_states'] )>0 ):
                    #note: 'final_states' are the states a gamma decay to
                    gam_cnt = 0     
                    for final_state in level['final_states'] :
                        Ei = level['Ex']
                        Ef = final_state
                        try:
                            gam = level['gammas'][gam_cnt]                      
                        except:
                            pdb.set_trace()
                        gammaE = gam['eng']   
                        s = "@Ei %6.3f%02d @Ef %6.3f%02d @color blue @I 10 @label %.f" \
                               %(Ei, idx, Ef, idx, gammaE) 
            
                        outStr += s + "\n"
                         
                        gam_cnt += 1
                s = ("#" + "="*78)
                outStr += s + "\n"     
        return outStr

    def __run_find_reference( self ):

        print("    ->FIND REFERENCES\n" )
        print( self.__print_selected_nuclei() )
        print("    --------------------------------\n\n")
        print("    proton=>p, beta=>b, gamma=>g, alpah=>a...")
        print("    Input the sting you want to search in the references. ex. d,p" )
        opt = input("Your choice: ")
        search_string = opt

        nuclei_list = self.__get_symbols() 
        nuclei_N = len(nuclei_list)
        outStr = ""
        
        
        nuclei_found = []
        nuceli_found_refs  = []
        
        # lopping
        for idx, nucleus, in zip( range(nuclei_N), nuclei_list ):
            print( "doing %4s : %d/%d" %(nucleus, idx+1, nuclei_N ) )
            
            isHaveData, content = self.__check_has_data(nucleus)
            if( not isHaveData ): continue

            

            # when we have data, then feed the parser data
            self.parser.feed( content )
      
            # get the experiment references which is a dic.
            # { 'A':'ref1', 'B': 'ref2'  }
            refs = self.parser.refs
            found_refs = [] 
            isFound = False;
            for key in refs.keys():
                ref_content = refs[key]
                if ref_content.find( search_string ) != -1:
                    found_refs.append( key )
                    isFound = True
                    outStr += "%5s:(%s) %s \n" %(nucleus,key, ref_content )
            
            if( isFound ):
                nuclei_found.append( nucleus )
                nuceli_found_refs.append( found_refs )
            
            #  reset and go to next nuclei.
            self.parser.reset()
        
        print("")
        print( outStr )
        opt = input("plot levels schemes for the states from above refs (y/N): " )
        
        if opt.lower() == 'y':
            self.__run_plot_lvl_schemes_with_found_refs( nuclei_found, \
                                                         nuceli_found_refs )

         
        pass

    def __run_plot_lvl_schemes( self ):
        print("    ->PLOT LEVEL SCHEMES\n" )
        print( self.__print_selected_nuclei() )
        print("    --------------------------------\n\n")

        nuclei_list = self.__get_symbols() 
        nuclei_N = len(nuclei_list)
        opt = "1"
        if nuclei_N > 5:
            print("    You have more than 5 nuclei to plot..." )
            print("    (1) use first 5 nuclei only (2) to plot ALL " )
            opt = input("Your choice: ")

        if opt == "1":
            nuclei_list = nuclei_list[:5]
            nuclei_N = len(nuclei_list)

        # upper energy limit control
        if self.lvlE_limitU == -1: 
            upperLimt = 999999.
        else: upperLimt = self.lvlE_limitU 


        outStr ="" 
        outStr2 = ""

        for idx, nucleus in zip( range(nuclei_N), nuclei_list ):
        
            print( "doing %4s : %d/%d" %(nucleus, idx+1, nuclei_N ) )
            
            isHaveData, content = self.__check_has_data(nucleus)
            if( not isHaveData ): continue
             
            # when we have data, then feed the parser data
            self.parser.feed( content )
            
            # retrieve data
            levels = self.parser.get_levels()
            
            # collect lvl input data.
            outStr += self.__convert_to_lvl( levels, 0, upperLimt, idx, nuclei_N )
            
            # collect nuclei data for band text
            # here we don't exclude nuclei with 0 level output.
            outStr2 += '%d \t "%s"\n' %(idx, nucleus )  


                      
            #  reset and go to next nuclei.
            self.parser.reset()
        #---------------------------------------- end of for loop

        # print( outStr )
        self.__write_out_results_and_use_lvl_builder( outStr, outStr2 )


    def __run_plot_lvl_schemes_with_JPIs( self):
        print("    ->PLOT LEVEL SCHEMES WITH SPIN AND PARITY\n" )
        print( self.__print_selected_nuclei() )
        print("    --------------------------------\n\n")

        print("    input the JPi, ex. 2+, or just +  (separate by spaces)  ")
        opt = input("Your Choice : ")
        JPIs = opt.split()
        
        print("")
        print("    input the minium num for JPi states (separate by spaces)")
        opt = input("Your Choice : ")
        JPINs = []
        for jpi in opt.split():
            jpi = int(jpi)
            JPINs.append( jpi )


        nuclei_list = self.__get_symbols() 
        nuclei_N = len(nuclei_list)
        opt = "1"
        if nuclei_N > 5:
            print("    You have more than 5 nuclei to plot..." )
            print("    (1) use first 5 nuclei only (2) to plot ALL " )
            opt = input("Your choice: ")

        if opt == "1":
            nuclei_list = nuclei_list[:5]
            nuclei_N = len(nuclei_list)

        # upper energy limit control
        if self.lvlE_limitU == -1: 
            upperLimt = 999999.
        else: upperLimt = self.lvlE_limitU 

        outStr ="" 
        outStr2 = ""

        for idx, nucleus in zip( range(nuclei_N), nuclei_list ):
        
            print( "doing %4s : %d/%d" %(nucleus, idx+1, nuclei_N ) )
        
            isHaveData, content = self.__check_has_data(nucleus)
            if( not isHaveData ): continue
             
            # when we have data, then feed the parser data
            self.parser.feed( content )
            
            # retrieve data
            levels = self.parser.get_levels()
            level_N = len( levels )
        
            # collect nuclei data for band text
            outStr2 += '%d \t "%s"\n' %(idx, nucleus )

            # for state counting.
            cnt_JPIs = [ 0 for _ in range( len(JPIs) ) ] 
            
            if( nuclei_N == 1 ): 
                # for one nuclei case.
                bandN = "0_5" 
            else: 
                bandN = "%d" %idx


            for  level in  levels :        
                s=""
                # Levels
                if( 'Ex' in level and level['Ex'] <= upperLimt and \
                    self.__check_JPI( cnt_JPIs, JPINs ) ):
                    
                    if( self.show_gam and 'spin' in level):
                        # when use gam, we need to have full levels.
                        s = "@lvlE %7.3f%02d @bandN %s @spin %s "\
                            %(level['Ex'], idx, bandN, level['spin'] )
                    
                    # no spin info case.                   
                    if( 'spin' not in level or level['spin'] == "" ):
                        s = "@lvlE %7.3f%02d @bandN %s " %(level['Ex'], idx, bandN )

                    # the states that match our JPIs    
                    for ii in range( len(JPIs) ):
                        if( 'spin' in level and level['spin'].find( JPIs[ii] ) != -1):
                            s = "@lvlE %7.3f%02d @bandN %s @spin %s "\
                            %(level['Ex'], idx, bandN, level['spin'] )
                            cnt_JPIs[ii] += 1
                    
                    if( len(s)> 0 ):        
                        outStr += s + "\n" 

                    if( not self.show_gam ): 
                        if( len(s)> 0 ): 
                            s = ("#" + "="*78)
                            outStr += s + "\n"
                        continue

                    # Gammas
                    #'final_states' are the states the gammas decay to
                    if( 'final_states' in level.keys() and \
                        len(level['final_states'] )>0 ):
                        
                        gam_cnt = 0     
                        for final_state in level['final_states'] :
                            Ei = level['Ex']
                            Ef = final_state
                            
                            gam = level['gammas'][gam_cnt]
                            gammaE = gam['eng']   
                            s = "@Ei %8.3f%02d @Ef %8.3f%02d @label %8.f @color blue" \
                                %(Ei, idx, Ef, idx, gammaE)        
                            if( self.show_gam ): outStr += s + "\n"
                            gam_cnt += 1

                    s = ("#" + "="*78) # separation line.
                    outStr += s + "\n"
                #  reset and go to next nuclei.
                self.parser.reset()
            #---------------------------------------- end of for loop

        # print( outStr )
        self.__write_out_results_and_use_lvl_builder( outStr, outStr2 )
    

    def __run_plot_lvl_schemes_with_stateN( self ):
        print("    ->PLOT LEVEL SCHEMES WITH # OF STATES\n" )
        print( self.__print_selected_nuclei() )
        print("    --------------------------------\n\n")

        nuclei_list = self.__get_symbols() 
        nuclei_N = len(nuclei_list)
        opt = "1"
        if nuclei_N > 5:
            print("    You have more than 5 nuclei to plot..." )
            print("    (1) use first 5 nuclei only (2) to plot ALL " )
            opt = input("Your choice: ")

        if opt == "1":
            nuclei_list = nuclei_list[:5]
            nuclei_N = len(nuclei_list)

        stateNs = []    
        print("    input the # of states for each select nucleus  (separate by spaces)  ")
        print("    or one number for all selected nuclei")
        opt = input("Your Choice : ")
        
        opt = opt.split()
        if len(opt) == 1:
            stateNs = [ int(opt[0]) for _ in range( nuclei_N )  ]   
        else:
            for stateN in opt:
                stateN = int(stateN)
                stateNs.append( stateN )

            # to avoid missing, we fill the last item for missing ones.
            if len(stateNs) < nuclei_N:
                ndiff = nuclei_N - len(stateNs)
                lastItem = stateNs[-1]
                for ii in range( ndiff ):
                    stateNs.append( lastItem )


        # upper energy limit control
        if self.lvlE_limitU == -1: 
            upperLimt = 999999.
        else: upperLimt = self.lvlE_limitU 

        outStr ="" 
        outStr2 = ""


        for idx, nucleus in zip( range(nuclei_N), nuclei_list ):
        
            print( "doing %4s : %d/%d" %(nucleus, idx+1, nuclei_N ) )
        
            isHaveData, content = self.__check_has_data(nucleus)
            if( not isHaveData ): continue
             
            # when we have data, then feed the parser data
            self.parser.feed( content )
            
            # retrieve data
            levels = self.parser.get_levels()
            
            if( nuclei_N == 1 ): 
                # for one nuclei case.
                bandN = "0_5" 
            else: 
                bandN = "%d" %idx
        
            # collect nuclei data for band text
            outStr2 += '%d \t "%s"\n' %(idx, nucleus )

            # for state counting.
            cnt_stateN = 0
            
            for  level in  levels :        
                s=""
                # Levels
                if(  cnt_stateN < stateNs[idx] ):
                    
                    # to avoid rare abnormal cases.
                    if( 'Ex' not in level ): continue
                    

                    cnt_stateN += 1 
                    
                    if( 'spin' not in level or level['spin'] == "" ):
                    # no spin info case.                   
                        s = "@lvlE %7.3f%02d @bandN %s " %(level['Ex'], idx, bandN )
                    else:
                        s = "@lvlE %7.3f%02d @bandN %s @spin %s "\
                            %(level['Ex'], idx, bandN, level['spin'] )
                           
                    if( len(s)> 0 ):        
                        outStr += s + "\n" 

                    if( not self.show_gam ): 
                        if( len(s)> 0 ): 
                            s = ("#" + "="*78)
                            outStr += s + "\n"
                        continue

                    # Gammas
                    #'final_states' are the states the gammas decay to
                    if( 'final_states' in level.keys() and \
                        len(level['final_states'] )>0 ):
                        
                        gam_cnt = 0     
                        for final_state in level['final_states'] :
                            Ei = level['Ex']
                            Ef = final_state
                            
                            gam = level['gammas'][gam_cnt]
                            gammaE = gam['eng']   
                            s = "@Ei %8.3f%02d @Ef %8.3f%02d @label %8.f @color blue" \
                                %(Ei, idx, Ef, idx, gammaE)        
                            if( self.show_gam ): outStr += s + "\n"
                            gam_cnt += 1

                    s = ("#" + "="*78) # separation line.
                    outStr += s + "\n"
                #  reset and go to next nuclei.
                self.parser.reset()
            #---------------------------------------- end of for loop

        # print( outStr )
       
        self.__write_out_results_and_use_lvl_builder( outStr, outStr2 )
    
    def __run_plot_lvl_schemes_with_found_refs( self, \
        nuclei_found, nuceli_found_refs ):
        '''
        we don't show gammas since we may miss some states
        if we select states from referenes.
        '''

        nuclei_list = nuclei_found
        nuclei_N = len(nuclei_list)

        
        # control the number of nuclei to plot
        opt = "1"
        if nuclei_N > 5:
            print("    You have more than 5 nuclei to plot..." )
            print("    (1) use first 5 nuclei only (2) to plot ALL " )
            opt = input("Your choice: ")

        if opt == "1":
            nuclei_list = nuclei_list[:5]
            nuclei_N = len(nuclei_list)

        # upper energy limit control
        if self.lvlE_limitU == -1: 
            upperLimt = 999999.
        else: upperLimt = self.lvlE_limitU 

        
        outStr = ""
        outStr2 = ""   

        for idx, nucleus in zip( range(nuclei_N), nuclei_list ):
        
            print( "doing %4s : %d/%d" %(nucleus, idx+1, nuclei_N ) )
         
            isHaveData, content = self.__check_has_data(nucleus)
            self.parser.feed( content )
            
            # retrieve data
            levels = self.parser.get_levels()

            # collect nuclei data for band text
            outStr2 += '%d \t "%s"\n' %(idx, nucleus )

            if( nuclei_N == 1 ): 
                # for one nuclei case.
                bandN = "0_5" 
            else: 
                bandN = "%d" %idx

            for  level in  levels :        
                s=""
                
                # Levels
                if(  level['Ex'] <= upperLimt and\
                self.__check_ref( level['ref'], nuceli_found_refs[idx])  ):
                     
                    if( 'spin' not in level or level['spin'] == "" ):
                    # no spin info case.                   
                        s = "@lvlE %7.3f%02d @bandN %s " %(level['Ex'], idx, bandN )
                    else:
                        s = "@lvlE %7.3f%02d @bandN %s @spin %s "\
                            %(level['Ex'], idx, bandN, level['spin'] )
                           
                    if( len(s)> 0 ):        
                        outStr += s + "\n" 

                    
                    if( len(s)> 0 ): 
                        s = ("#" + "="*78)
                        outStr += s + "\n"
                     
                    
                
                #  reset and go to next nuclei.
                self.parser.reset()
            #---------------------------------------- end of for loop

        # print( outStr )
       
        self.__write_out_results_and_use_lvl_builder( outStr, outStr2 )

        pass

    def __run_plot_lvl_schemes_with_rec_eng( self ):
        print("    ->PLOT LEVEL SCHEMES WITH REACTION ENERGY LIMTS\n" )
        print( self.__print_selected_nuclei() )
        print("    --------------------------------\n\n")

        print("    gs  = ground state energy = 0.     [keV]  ")
        print("    Sn  = 1 neutron separation energy  [keV]  ")
        print("    Sp  = 1 protron separation energy  [keV]")
        print("    S2n = 2 neutron separation energy  [keV]")
        print("    S2p = 2 protron separation energy  [keV]")
        print("    Sa  = 1 alpha separation energy (Sa = -Qa) ")
        print("    input format as 'Sn' , 'Sn + 500'   ")
        print("    ")

        lowE = input("Your lower energy limit : ")
        lowE_shift = 0.

        if( lowE.find("+") != -1 ):
            lowE = lowE.split("+")
            lowE_type  = lowE[0]
            lowE_type  = lowE_type.strip()
            lowE_shift = float( lowE[1] )
        elif( lowE.find("-") != -1 ):
            lowE = lowE.split("-")
            lowE_type  = lowE[0]
            lowE_type  = lowE_type.strip()
            lowE_shift = -1*float( lowE[1] )
        else:
            lowE_type  = lowE
            lowE_type  = lowE_type.strip()
        if lowE_type not in ( "gs", "Sn","S2n", "Sp", "S2p", "Sa" ):
            print( "%s is invalid input format" %lowE ) 
            input( "press any key to continue ")
            return

        uppE = input("Your upper energy limit : ")
        uppE_shift = 0.
        if( uppE.find("+") != -1 ):
            uppE = uppE.split("+")
            uppE_type  = uppE[0]
            uppE_type  = uppE_type.strip()
            uppE_shift = float( uppE[1] )
        elif( uppE.find("-") != -1 ):
            uppE = uppE.split("-")
            uppE_type  = uppE[0]
            uppE_type  = uppE_type.strip()
            uppE_shift = -1*float( uppE[1] )
        else:
            uppE_type  = uppE
            uppE_type  = uppE_type.strip()

        if uppE_type not in ( "gs", "Sn","S2n", "Sp", "S2p", "Sa" ):
            print( "%s is invalid input format" %uppE ) 
            input( "press any key to continue ")
            return

        # control the number of nuclei to plot.
        nuclei_list = self.__get_symbols() 
        nuclei_N = len(nuclei_list)
        opt = "1"
        if nuclei_N > 5:
            print("    You have more than 5 nuclei to plot..." )
            print("    (1) use first 5 nuclei only (2) to plot ALL " )
            opt = input("Your choice: ")

        if opt == "1":
            nuclei_list = nuclei_list[:5]
            nuclei_N = len(nuclei_list)
        

        outStr ="" 
        outStr2 = ""
         

        for idx, nucleus in zip( range(nuclei_N), nuclei_list ):
        
           
            isHaveData, content = self.__check_has_data(nucleus)
            if( not isHaveData ): continue
             
            # when we have data, then feed the parser data
            self.parser.feed( content )
            
            # retrieve data
            levels = self.parser.get_levels()
            
            # we have to make sure 'Sn', 'Sp'... data exit.
            # good_status = true tell us, we can get these numbers.
            lowerLimt, upperLimt, good_status  = \
            self.__get_eng_limits(  nucleus, \
                                    lowE_type, lowE_shift, \
                                    uppE_type, uppE_shift )

            
            if good_status:  
                # collect lvl input data.
                outStr += self.__convert_to_lvl(  levels, lowerLimt, upperLimt, \
                                                  idx, nuclei_N, forceNoGam = True )
            
                
            # collect nuclei data for band text
            outStr2 += '%d \t "%s"\n' %(idx, nucleus )  
            
            # note: if we want to eliminate the text for empty levels.
            # use ==> if( self.levelN_output > 0 ):
            # levelN_output will be update at __convert_to_lvl()
            

            print ( "doing %4s : %2d/%2d energy range = %5.f to %5.f [keV]" \
                    %(nucleus, idx+1, nuclei_N, lowerLimt, upperLimt )  )

                   
            #  reset and go to next nuclei.
            self.parser.reset()
        #---------------------------------------- end of for loop

        
        self.__write_out_results_and_use_lvl_builder( outStr, outStr2 )


        pass

 

    
    

if __name__ == '__main__':
     
    obj = Run()

    
