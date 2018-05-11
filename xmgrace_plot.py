import subprocess           # for calling xmgrace to plot.
import copy
import math
import mytool 
 
class PRE_Separate_levels( object ):
    
    def __init__(self, list_lvl, dim):
        ''' It take a list of levels
        each element is a dic, and we have keys:
        'lvlE', and 'bandN', we will use these two to do level separation.
        '''
        self.__list_lvl = list_lvl
        self.__length = dim[0]
        self.__font_size = dim[1]
        self.__bandL_list = []
        self.__bandU_list = [] # may be I won't use it.
        
        #
        #  to examine the overlap of a text, we have to make sure
        #  both x and y location. x location will be determined by the bandL 
        for lvl in self.__list_lvl:
            
            bandN = lvl['bandN']
            band = bandN.split("_") 
            n = len( band )
            if( n>1 ):
                bandL = int ( band[0] )
                bandU = int ( band[1] )
                lvl['bandL'] = bandL
                lvl['bandU'] = bandU
                self.__bandL_list.append( bandL ) # not used, but save it.
            else:
                lvl['bandL'] = int( bandN )
                lvl['bandU'] = int( bandN )
                self.__bandL_list.append( int(bandN) ) # not used, but save it.

            lvl['textY'] = float(lvl['lvlE']) # assign the initial value.
        
         
        # to set the text height value
        # the formula is from my empirical test
        self.__text_height = self.__font_size/1000 * 250 * self.__length/1000
        
        
        
        self.Check_level_overlap()
        
        self.modify_level()
        
        
        #===================================================
        
        
        
                    
    def Get_textY_min_max(self):
        """ to get the min/max text y position"""
        self.__textY_MAX = 0
        self.__textY_MIN = 9999999
        
        for lvl in self.__list_lvl:
            if( lvl['textY'] >self.__textY_MAX ): self.__textY_MAX = lvl['textY']
            if( lvl['textY'] <self.__textY_MIN ): self.__textY_MIN = lvl['textY']    
            pass
        return self.__textY_MIN, self.__textY_MAX 
        #print( "TEST: textY max = ", self.__textY_MAX, "textY min = ", self.__textY_MIN )
        #print( "TEST: lvlE max = ",  self.__list_lvl[-1]['lvlE'], \
        #             "lvlE min = ",  self.__list_lvl[0]['lvlE'] )
        
       



    def set_text_separate_value(self, text_height):
        ''' Let user to input text_height.
        '''
        self.__text_height = text_height     
    
                      
                      
    def Check_level_overlap(self ):
        """ adding 'overlap' key to each element of list_lvl
        and check what the levels are overlapping a given level.
        """
        idx = 0 
        for lvl1 in self.__list_lvl  :
            
            textY = float( lvl1['textY'] )
            
            # create a sub list to second loop. here [:] is a new one.
	    # We exclude the lvl1 in the sub_list, in order to compare
	    # lvl2 level ( to avoid self-confilct )
            sub_list = self.__list_lvl [:] 
            del sub_list[idx]
            idx +=1 

	    # set initial values: no overlap 
            isOverLap = False
            lvl1['olap_lvl'] = []
            for lvl2 in sub_list:
                
		# conditions for overalping: 
		# (1) the y separation of two text label less than text height
		# (2) the two text labels are not from the two states with 
		#     exact the same energy. They cannot be separated. 
		# (3) the states have the same starting band index.
                
                check1 = abs( textY - float( lvl2['textY'] )) <= self.__text_height
                check2 = ( lvl1['lvlE'] !=  lvl2['lvlE'] )
                check3 = ( lvl1['bandL'] == lvl2['bandL'] )
                checkALL = ( check1 and check2 and check3 )
                if ( checkALL ) :
                    lvl1['overlap'] = 'Yes'
                    lvl1['olap_lvl'].append( lvl2['textY'] )
                    isOverLap = True 
                     
                pass # end of the second for, for sub_list
             
            # after check the elemnts now, we can set the non-overlap situation.
            if isOverLap == False: 
                lvl1['overlap']="none"
                lvl1['olap_lvl'] = [] 
            
        pass # end of the first for, for self.__list_lvl


 
 


    def isAllgood( self):
        """ to check is there is no more overlapped levels. """
        for lvl in self.__list_lvl:
            if ( lvl['overlap'] == "Yes" ): return False
        return True          



 
    def modify_level(self):
        """ to modify the text spacing. """
    
        go_on = True 
        step = 0 # for protecting purpose.
        
        
        while( go_on ):
         
            for i in range( len(self.__list_lvl) ): 
            
                lvl = self.__list_lvl[i] # short-handed notation.
                
                #-------------------------------------------------------------------|
                # note: if ['olap_lvl'] is empty, then min() will casue ValueError.
                #
                if len( lvl['olap_lvl'] ) > 0:  
                    
                    #print( 'step=',step,
                    #    'overlap_lvls =',lvl['olap_lvl'], 
                    #    'lvlE=' , lvl['lvlE'],
                    #    'textY=', lvl['textY']) 
                    
                    if min( lvl['olap_lvl'] ) > lvl['textY'] :
                        # this block only applies to the lowest level
			# among the of the group of the overlapped states.
			# move the lowest text label even lower
                        lvl['textY'] -= 5
                        
            
                    if max( lvl['olap_lvl'] ) < lvl['textY'] :
                        # this block only applies to the highest level
			# among the of the group of the overlapped states.
			# move the highest text label even higher
                        lvl['textY'] += 5
                        
            
                
                #----------------------------------------- re-check the overlap situation.
                self.Check_level_overlap()
                

                #-------------------------------------- exit if there no more overlapping.
                if ( self.isAllgood( ) ):
                    go_on = False   # to exit  the while loop.
                    break           # to break the for loop.
                pass # end of "for" 
            
            #-------------------------------- for proventing infinite loop.
            step += 1
            if (step+1) > 5000: go_on = False 
            #--------------------------------
        pass # end of while 
            
         

 




class PRE_Parse_gamma_level( object ):
    '''This class is used to parse the gamma ray (no plot part yet)
    We need both gamma and level list to do the calculations.
    
    variable explanation:
    self.__lvl_list is a list, each element is a dic
    -- key: 'bandN' (ex. 0_5 ) is for the band setting.
    -- key: 'lvlE'  (ex. 100) is for the energy of a level.
    -- key: 'color' (ex. red) is for the color of a level.
    -- key: 'spin'  (ex. 3+ ) is for the spin of a level.
    -- key: 'xi' and 'xf'  are for the x coordinates.
    '''
    
    
    def __init__(self, lvl_list, gam_list, bandL_list, bandU_list,  par ):
        self.__lvl_list = lvl_list 
        self.__gam_list = gam_list
        self.__bandL_list = bandL_list
        self.__bandU_list = bandU_list
        self.__par = par
        self.__bandspacing = par.bandspacing

        # to assign idx and gammaE to our gammas, 
        # idx will help us to find the gamma easier.
        gam_idx = 0
        for gam in self.__gam_list:
            gam['idx'] = gam_idx
            gam['gammaE'] = float( gam['Ei'] ) - float( gam['Ef'] )
            gam['crossBand'] = False
            gam_idx += 1
        
       
        self.Parse() 



    def Parse(self):
        ''' the main core of parsing. It prepares the xi and xf info '''
        lvl_list = self.__lvl_list
        gam_list = self.__gam_list
        
        
        # assign the the E_i and E_f lvl info into each gam
        # ex. gam['Ei_xi'] = 1000, gam['Ei_xf'] = 2000, .. for both Ei and Ef.
        self.SetEiEf() 
        
        
        
        # calculate the overlap x range 
        # ie. calculate which x range of Ei and Ef would overlap for a given gamma ray.
        # if Ei level spans (10-20 ) and Ef level(10-30), then the overlap range is (20-30) 
        overlap_range_list = self.Cal_overlap_range() 
        
        if(0):
            for temp in overlap_range_list: print( temp )
        
        
        
        # initialization for xi and xf of a gamma ray 
        # xi and xf are very important keys.
        for gam in gam_list:
            if ( gam['overlap'] ):
                #
                #  if Ei and Ef levels are overlapped, then set the gamma 
                #  at it middle of its overlapped range 
                #  . Note, it is just the initial setting.
                #
                gam['xi'] =  ( gam['overlap_range_xi'] + gam['overlap_range_xf'] )/ 2.0
                gam['xf'] =  ( gam['overlap_range_xi'] + gam['overlap_range_xf'] )/ 2.0

            else:
                #
                # This part is for the gammas for cross band case.
                self.Cal_cross_band( gam ) 
                
      

      
            
        # to group gammas within the same x overlap range.
        # ie. we group the gammas with the same overlap xi-xf range 
        # into a subgroup
        # gam1's Ei and Ef has overlapped range at 20-30
        # gam2's Ei and Ef has overlapped range at 20-30
        # then gam1 and gam2 are in the same subgroup of the same x range.
        subgroups = self.Cal_subgroups( overlap_range_list )
        if( 0 ): print ( subgroups )
        
        # now the subgroup look like
        # [ [0, 1, 2, 3, 10],  
        # [4, 5, 6, 7, 8, 9, 11] ]
        # the numbers are the gammas' idx, and we have two X groups.  
 
  
        
        # even within a subgroup of the same xi-xf range, 
        # some gamma would overlap with the same yi-yf range, but some don't 
        # so we need grouping in Y (vertical grouping) in addition to 
        # horizontal grouping. ( this process is rather complicated. )   
        if(0): print( "-----------test vertical grouping------")
        
        subgroups_new = []
        for subgroup in subgroups:
           subgroup_temp = self.Cal_sugroupV( subgroup )
           for item in subgroup_temp:
               subgroups_new.append(item)
        
        
        subgroups = copy.deepcopy( subgroups_new ) 
        # now the subgroups will look like:
        # [[0, 1, 2], [3], [10]]       <-- have 3 Y groups, in X group1 
        # [[4], [5], [6, 7, 8, 9, 11]] <-- have 3 Y groups, in X group2

       
       
       
       
        # to separate lines in a subgroup according to X and Y grouping.
        # this method will also update the self.__gam_list
        self.Separate_gamma_line( subgroups)


                                   
        #____________________done with parsing____________________
        pass



 
    
    def Update(self):
    
        return self.__lvl_list, self.__gam_list
        pass
    

         
    def isInRange(self, xia, xfa, xib, xfb):
        ''' Return true when two lines overlap, 
            index i, f for two lines,
	    index a, b for the two ends.
	'''
        result = True
        if( xia >= xfb) or ( xfa <= xib): result = False    
        return result
    

    def isInRange2(self, xia, xfa, xib, xfb):
        ''' Return true when two lines overlap, 
            index i, f for two lines,
        index a, b for the two ends.
    '''
        result = True
        if( xia > xfb) or ( xfa < xib): result = False    
        return result
    
    
    def isInRangeY(self, yia, yfa, yib, yfb):
        ''' Return true when two yi-yf interval overlap'''
        result = True
        if( yia <= yfb ) or ( yfa >= yib ): result = False   
        
        return result
    
    
    def GetBandL_U( self, lvlE ):
        """ serach a lvl's bandL and bandU by its lvl E
        """
        bandL = -999
        bandU = -999

        for lvl in self.__lvl_list:
            if lvlE == lvl['lvlE']:
                bandL = lvl['bandL']
                bandU = lvl['bandU']
                return bandL, bandU

        return bandL, bandU



    def Getgam(self, idx):
        ''' From  idx to get corresponding gam dictionary'''
        temp = {}
        for gam in self.__gam_list:
            if gam['idx'] == idx: temp = gam
        return temp
    
    
    def GetEiEf(self, idx):
        ''' From gamma's idx to get its Ei and Ef '''
        Ei =0
        Ef =0
        for gam in self.__gam_list:
            if gam['idx'] == idx:
                Ei = gam['Ei']
                Ef = gam['Ef']
                #note: now Ei and Ef are in Str 
                
        return float(Ei), float(Ef)
        

    def SetEiEf(self):
        ''' ex. gam['Ei_xi'] = 1000, gam['Ei_xf'] = 2000, .. 
            for both Ei and Ef. 
        '''
        lvl_list = self.__lvl_list
        gam_list = self.__gam_list
        
        # assign the the E_i and E_f lvl info into gam
        for lvl in  lvl_list:
            for gam in gam_list:

                if lvl['lvlE'] == gam['Ei']:
                    gam['Ei_xi'] =lvl['xi'] 
                    gam['Ei_xf'] =lvl['xf'] 

                if lvl['lvlE'] == gam['Ef']:
                    gam['Ef_xi'] =lvl['xi'] 
                    gam['Ef_xf'] =lvl['xf'] 
                    
               
                     

        # here, since we pass by reference, and so we also update the 
        # self.__lvl_list and self.__gam_list, it is equal to 
        #self.__lvl_list = lvl_list
        #self.__gam_list = gam_list
        
        pass
    
    def Cal_overlap_range(self):
        '''to cal which x range Ei and Ef would overlap for a given gamma ray.'''
        
        gam_list = self.__gam_list # for short-handed notation.
        overlap_range_list = []
        
        # we check the common x range between initial and final state for
        # each gamma ray, we also add new keys.

        # instead of checking xi-xf range, we should check the 
        # bandL and bandU 
        # since the wedge shape will shink the level.
        for gam in gam_list:
            Ei_bandL, Ei_bandU = self.GetBandL_U( gam['Ei'] )
            Ef_bandL, Ef_bandU = self.GetBandL_U( gam['Ef'] )


            if not self.isInRange2( Ei_bandL, Ei_bandU, \
                                   Ef_bandL, Ef_bandU ):
                gam['overlap'] = False
                gam['overlap_range'] = 0 
                 
            else:
                gam['overlap'] = True
                 
                ########################
                
                overlap_bandL = max( Ei_bandL, Ef_bandL )
                overlap_bandU = min( Ei_bandU, Ef_bandU )

                gam['overlap_range_xi']  = self.__bandL_list[ overlap_bandL ]
                gam['overlap_range_xf']  = self.__bandU_list[ overlap_bandU ]
                #######################
                temp_tuple = ( gam['idx'], \
                               gam['overlap_range_xi'], \
                               gam['overlap_range_xf'])
                overlap_range_list.append( temp_tuple )


        
        self.__gam_list = gam_list
        return overlap_range_list
        pass




    def Cal_subgroups(self, overlap_range_list):
        ''' we group the gammas with the same overlap xi-xf range 
        into a subgroup'''
        subgroups = []
        for i in range( len( overlap_range_list ) ):
            temp_subgroup = []
            idxa = overlap_range_list[i][0]
            x_ia = overlap_range_list[i][1]
            x_fa = overlap_range_list[i][2]
            temp_subgroup.append( idxa )
            
            # test with oter members
            for j in range( len( overlap_range_list ) ):
                idxb = overlap_range_list[j][0]
                x_ib = overlap_range_list[j][1]
                x_fb = overlap_range_list[j][2]

                # check both two end points i_______f 
                if i != j and ( x_ia == x_ib ) and (x_fa == x_fb) : 
                    temp_subgroup.append( idxb )
                    pass
                
                # check just start  point i_______  or end point _____f
                # if i != j and ( ( x_ia == x_ib ) or ( x_fa == x_fb ) ): 
                #     temp_subgroup.append( idxb )
                #     pass
            
            # to sort the list.
            temp_subgroup.sort( key= lambda x: x ) # f(x) = x
            
            # we only want the cases with 2 or more        
            if ( len(temp_subgroup) > 1  and temp_subgroup not in subgroups ): 
                subgroups.append( temp_subgroup )      
        return subgroups         
        pass



    def Cal_sugroupV(self, subgroupX ):
        ''' given a subgroupX, further separate them according Y overlapping.'''
        Vgroups = []
        
        ## testing y overlapping
        for g_idxa in subgroupX:
            Vgroup=[]
            Vgroup.append(g_idxa) 
            yi_a, yf_a = self.GetEiEf( g_idxa )
            overlap_yi_a = yi_a
            overlap_yf_a = yf_a
            # we want to compare g_idxa with the other members.
            
            
            for g_idxb in subgroupX:
    
                if(g_idxa != g_idxb):
                    
                    yi_b ,yf_b = self.GetEiEf(g_idxb )
                    
                    if self.isInRangeY( overlap_yi_a, overlap_yf_a, yi_b ,yf_b ):
                        # update the overlapping range:
                        overlap_yi_a = max( overlap_yi_a, yi_b)
                        overlap_yf_a = min( overlap_yi_a, yf_b)
                        Vgroup.append( g_idxb)
                        pass
                    pass
                pass
            # to sort the list according its gammaE
            Vgroup.sort( key= lambda x:x )  
            if( Vgroup not in Vgroups): Vgroups.append( Vgroup )
            pass
        
       
        # sometimes, the order of the gamma ray will fool the overlapping 
        # detection so I need to check it again.
    
         
        Vgroups_new=[]
        #
        #  to detect whether we have common items.
        #
        for list1 in Vgroups:
            for list2 in Vgroups:
                
                having_same_item = False
                
                # the follwoing is just to compare each items 
                if ( list1 != list2 ):                  
                    for item1 in list1:
                        for item2 in list2:
                            if ( item1 == item2 ): 
                                having_same_item = True
                                
                # after comparing, we put the common item into list1                  
                if ( having_same_item ):
                    for item2 in list2:
                        if (item2 not in list1 ): 
                            list1.append( item2 )
                            
            list1.sort( key= lambda x:x )                    
            if( list1 not in Vgroups_new): Vgroups_new.append( list1 )   
        
        # now the vertical grouping is good.
        return Vgroups_new


   
    def Separate_gamma_line(self, subgroups):
        ''' accoring to X and Y grouping, we separate the lines equally.
            Note: initially, we just put the line in the middle of 
            overlapped range of X.  That will cause several line overlap 
            each other.'''

        for subgroup in subgroups: 
            
            if(0):print("============================")
            if(0):print( "TEST subgroupV = ", subgroup)
             
            gamma_to_adust_list = [] 
            # a temp container for the idx 
            # for the gammas in a subgroupV we want to adjust
            
            #
            # we only need to adjust when we have two more gammas
            # in a subgroupV
            if ( len(subgroup) > 1 ):
                for idx in subgroup:
                    # retrieve the gam{} dictionary, from self.__gam_list
                    gam_temp = self.Getgam( idx ) 
                    gamma_to_adust_list.append( gam_temp )
                    pass
                
                
                # to sort the gamma list according its Ei
                gamma_to_adust_list.sort( key= lambda x:x['Ei'], reverse=True ) 
                
                # calculations for saving space
                # we will update 'gamma_to_adust_list'
                # it is a subgroup of list_gam 
                N_of_sections, gamma_to_adust_list = \
                self.sort_gamma_to_save_space(gamma_to_adust_list)
                
                
                #
                # preparation for the adjustment
                #
                x_start = float( gamma_to_adust_list[0]['overlap_range_xi'] )
                x_end   = float( gamma_to_adust_list[0]['overlap_range_xf'] )
                interval = (x_end - x_start) / N_of_sections
                times = -1
                 
                 
                # we use the element in 'gamma_to_adjust_list'
                # to help us assign the xi and xf,
                # in this way, we would not add the keys that are only used for the 
                # calculations into the gam dictionary.
                #
                for item in  gamma_to_adust_list:
                    idx = item['idx']
                    gam = self.Getgam(idx)
                    
                    
                    gam['xi'] = \
                    gam['xf'] = x_start + interval*( item['section']+1 ) \
                            + self.__par.minorShift * item['shift']
                    if(0 ): 
                        print( "section = ", item['section'], "gamE =", gam['gammaE'] ) 

        pass # end of Separate_gamma_line()

    

    
    
    

    ###########################################################################
    #   @detail 
    #   this function will update the gam (which is a dictionary)in the 
    #   "gamma_to_adjust" list, in which all the gammas are in the same 
    #   X-subgroup and Y-subroup. 
    #   
    #   we add two new keys 'section' and 'shift' to the gam.
    #   These two keys are used to separated the gammas. 
    #   'section' is for the major poisition.
    #   'shift' is a minor adjustment.
    #    
    #
    def sort_gamma_to_save_space(self, gamma_to_adjust):
        """ 
            to sort and group the gam objects to save space.
            we add 'section' key for the major poisition mark.
        """
        
        if(0):
            for gam in gamma_to_adjust:
                print( "Ei = %s, gammaE =%s " %( gam['Ei'], gam['gammaE'])  )
         
        #
        # to get the overlap y range for each subgroupV
        #
        y_high = -1
        y_low  = 9999999
        for gamma in gamma_to_adjust:
            if( float(gamma['Ei']) > y_high ): y_high = float( gamma['Ei'] ) 
            if( float(gamma['Ef']) < y_low ):  y_low =  float( gamma['Ef'] )     
             
        

        section = 0
        doneList = [] 
        
        gamma_to_adjust_new  = copy.deepcopy( gamma_to_adjust )
        
        while( len(gamma_to_adjust_new) >= 1 ):
          
            # get the gamma from the highest level which has the largest energy.
            # since it is the longest line, we should do its arrangement first.
            gamHL = self.__get_longest_highest_gam(gamma_to_adjust_new)
            if(0): print("============================================")
            if(0): print( "gammaE = %4.f for gamHL" %gamHL['gammaE'] )
            

            # remove the gamma in the original list, and put it into 'done' list.
            gamma_to_adjust_new.remove( gamHL ) 
            doneList.append( gamHL )  
            gamHL['section'] = section 


            # we could place other gammas under the gamma we just placed
            # only if the other gammas are lower.
            # we will update 'space' once we put a gam1 under the gamHL,
            # and then we can search other possible gam2 ot put underneath.

            space = float( gamHL['Ef'] )
            while( space > 0 ):
                # if gamHL directly decay to the ground state, definitely,
                # we don't have enough space to put other gammas.

                # use 'tmplist' to store possible gammas which are below the gamHL
                tmplist = [] 
                for gam in gamma_to_adjust_new:
                    
                    if(0):print( "space = %.f gam Ei = %s" %(space, gam['Ei'] ) )

                    if( float( gam['Ei'] ) <= space):
                        tmplist.append( gam )
                


                # to get the shortest gamma among all possible gammas in 'tmplist'
                # shortest_gam will use to point to the gam obj ( it is a dictionary)
                shortest_gamE = 999999
                shortest_gam = {}
                if( len(tmplist) > 0 ):    
                    for gam in tmplist:
                        if ( float(gam['gammaE']) < shortest_gamE ):
                            shortest_gam  = gam 
                            shortest_gamE = gam['gammaE']
                else:
                    # no suitable gammas
                    break
                


                #    
                # to update space.
                # for example, if we have 5000->2000 (so initally, we have space = 2000)
                # and we get 2000->1800 as our shortest gam below 2000 level,
                # we then update space to 1800.
                #
                if( len(tmplist) > 0 ):  
                    
                    shortest_gam['section'] = section
                    
                    space = float( shortest_gam['Ef'] )  # update the space.
                    
                    # put the shortest one to the 'done' list.
                    gamma_to_adjust_new.remove( shortest_gam )
                    doneList.append( shortest_gam )
                    if(0): print( "gammaE = %4.f for shortest_gam" %shortest_gam['gammaE'] )
                    
                pass #----- end of inner while loop.
            
            section += 1
            pass #------ end of outter while loop.
            
        
        sectionN = section + 1   #total number of sections to make division.


        #
        #  'shift' is for minor adjusment for the gams with the same 
        #  'section' value. the gams in the 'done' list has an ascendant 'section' value.
        #  for a given section, when we just have 1 gam, then shift = 0.
        #  if we have 3, 5, 7 ... gams in a given section, then the shift will be -2, -1, 0, 1, 2 
        #  if we have 2, 4, 6 ... gams in a given section, then the shift will be -2, -1, 1, 2

        # check the number of gam in a given section
        # we use a list 'num' to record the num of gams
        # the index refer to the 'section' value.
        #
        num     = [ 0 for _ in range(section ) ]
        for gam in doneList:
            num [ gam['section'] ] += 1
          
        
        tmp_idx = 0
         
        for gam in doneList:
            
            gam['shift'] = 0 # initialization
            
            # to skip just 1 gam case for a given 'section'
            if( num[ gam['section'] ]== 1 ): continue
 
            # when the idx < total number of gam in a given 'section'
            if( ( tmp_idx + 1 ) <= num[ gam['section'] ] ):
                gam['shift'] = self.Cal_shift( tmp_idx, num[ gam['section'] ] )
                tmp_idx += 1
            else:
                # we done a 'section', then reset idx to 0.
                tmp_idx = 0
             

            
        if(0):
            for gam in doneList:
                print( "Ei = %s gammaE = %s,  sect = %d, shift = %.2f" \
                       %(gam['Ei'], gam['gammaE'], gam['section'], gam['shift'] ) )
                      
        return sectionN, doneList
          
    


    def __get_longest_highest_gam(self, gamList):
        highest_Ei   = -1
        longest_gamE = -1 
        gammHi_longest = {}
        tempList = []
        
        # to get the highest Ei
        # and append all the gammas from the highest Ei to a temp list
        for gam in gamList:
            if( float( gam['Ei'] ) > highest_Ei):
                highest_Ei = float( gam['Ei'] )
                
        for gam in gamList:        
              if( float( gam['Ei'] ) == highest_Ei):
                tempList.append( gam)
                 
        
        # when we have multiple gamma from the highest level
        # we select the longest gamma      
        if( len(tempList) > 1):
            for gam in tempList:
                if( float( gam['gammaE'] ) > longest_gamE ):
                    longest_gamE = float( gam['gammaE'] )
                    gammHi_longest = gam
        else:
            longest_gamE = float( tempList[0]['gammaE'] )
            gammHi_longest = tempList[0] 
        
        del tempList
        return gammHi_longest
  
  
    
    def Cal_cross_band( self, gam ):



        gam['crossBand'] = True 
        bandsize = self.__par.bandwidth + 2*self.__par.bandspacing
        cross_limit = self.__par.auxBandLimit * bandsize

        # it looks like
        #            /=======
        #           /
        #  ======  V 
        # if the gamma's crossing is too long, we will have a dashed line.

        # note: I may need some corrections for the x position,
        # since arrow will need to shift the x as well.. not only y 


        if( gam['Ei_xi'] > gam['Ef_xf']  ):
            if(  (gam['Ei_xi']- gam['Ef_xf'] ) > cross_limit ):
	        # long crossing
                gam['xi'] =  gam['Ei_xi'] 
                gam['xf'] =  gam['Ei_xi']  - self.__bandspacing * 2
            else:
                # nearby crossing  
                gam['xi'] =  gam['Ei_xi']
                gam['xf'] =  gam['Ef_xf']
        

        
        # It looks like:
        # ========\
        #          \       
        #           V    ========
        # if the gamma's crossing is too long, we will have a dashed line.
        if( gam['Ei_xf'] < gam['Ef_xi']   ):
            
            if(  ( gam['Ef_xi'] -gam['Ei_xf'] ) > cross_limit ):
		# long crossing
                gam['xi'] =  gam['Ei_xf'] 
                gam['xf'] =  gam['Ei_xf'] + self.__bandspacing  * 2
            else:
                # nearby crossing
                gam['xi'] =  gam['Ei_xf']
                gam['xf'] =  gam['Ef_xi']
        
        
        #====================================================================
    



    #
    # to calculate the minor adjustment 'shift'
    # gamN = the n-th gam in a given 'section'
    # gamNtotal = total gam number in a given 'section'
    def Cal_shift(self, gamN, gamNtotal):

        # just to make sure gamN is the positive number.
        gamNtotal = int( abs(gamNtotal) )

        if( gamNtotal == 1 or gamNtotal == 0): 
            return 0

        elif( gamN < 0 ): 
            return 0

        elif( gamNtotal%2 == 0 ): 
            # for even
            # gamN =    0,    1,   2,   3
            #        -1.5, -0.5, 0.5, 1.5
            return gamN-(gamNtotal/2) + 0.5
        else:
            # for odd
            # gamN = 0,  1, 2, 3, 4
            #       -2, -1, 0, 1, 2
            return  gamN-(gamNtotal/2)
        pass




class Gamma(object):
    
    def __init__(self, gam, lvl_list, dim ):
        self.__gam      = gam
        self.__lvl_list = lvl_list
        self.__dim      = dim
        self.__angle    = 0   # label's angle for cross-band gam

        self.__Ei = "0"
        self.__Ef = "0"
        self.__xi = 0
        self.__xf = 0
        self.__I = 10
        self.__color = "black"
        self.__label = ""
        self.__linestyle = "1"
        self.__arrow = 1

        # gam is a dic, here we make sure the keys are really in it.
        if 'Ei'  in gam:  self.__Ei = gam['Ei']
        if 'Ef'  in gam:  self.__Ef = gam['Ef'] 
        if 'xi'  in gam:  self.__xi = gam['xi']
        if 'xf'  in gam:  self.__xf = gam['xf']   
        if 'I'   in gam:  self.__I  = gam['I']
        if 'linewidth' in gam:  self.__I =  float( gam['linewidth'] )   
        if 'label' in gam: self.__label = gam['label']                   
        if 'color' in gam:  self.__color = gam['color'] 
        if 'linestyle' in gam:  self.__linestyle =  gam['linestyle'] 
        if 'arrow' in gam:  self.__arrow =  int( gam['arrow'] )
        pass
    
    
    
    
    def Parse_color( self ):
        color = self.__color
        result =""        
        if color.lower()   == 'black': result = 'color 1'            
        elif color.lower() == 'red':   result = 'color 2'            
        elif color.lower() == 'green': result = 'color 3'
        elif color.lower() == 'blue':  result = 'color 4'        
        elif color.lower() == 'yellow':result = 'color 5'                    
        elif color.lower() == 'brown': result = 'color 6'            
        elif color.lower() == 'grey':  result = 'color 7'
        elif color.lower() == 'violet':result = 'color 8'        
        elif color.lower() == 'cyan':  result = 'color 9'
        elif color.lower() == 'magenta': result = 'color 10'
        elif color.lower() == 'orange':  result = 'color 11'
        elif color.lower() == 'indigo':  result = 'color 12'
        elif color.lower() == 'maroon':  result = 'color 13'
        elif color.lower() == 'turquoise': result = 'color 14'
        elif color.lower() == 'grey4':     result = 'color 15'            
        else: result =  'color 1'        
        self.__color = result  
    
    
     
    
    
    def Process(self):
        self.Parse_color()
         
        outStr = ""
        outStr += self.Get_gamma_line()
        outStr += self.Get_gamma_label()
        return outStr
        pass
    
    
    def Get_auxiliary_line( self ):
        """ to deal with the gamma ray when crossing over 1 band.              
        
        It looks like
        =====\
              \ 
               v ..........==============
                  aux line 
        """
        dash_line_xi = 0
        dash_line_xf = 0
        if( self.__gam['Ei_xi'] > self.__gam['Ef_xf'] ):
            dash_line_xi = self.__gam['Ef_xf']
            dash_line_xf = self.__gam['xf']  + self.__par.auxlineExt
           
        
        if( self.__gam['Ei_xf'] < self.__gam['Ef_xi'] ):
            dash_line_xi = self.__gam['xf'] - self.__par.auxlineExt
            dash_line_xf = self.__gam['Ef_xi']
            pass

        result = ""
        result += '@with line\n'
        result += '@    line on\n'
        result += '@    line loctype world\n'
        result += '@    line g0\n' 
        result += '@    line '  + str(dash_line_xi) + ',' + self.__Ef +',' \
                                + str(dash_line_xf)+ ', ' + self.__Ef +'\n'
        result += '@    line linewidth 1.0\n'
        result += '@    line color 7 \n'   # set it to gray   
        result += '@    line arrow 0 \n'
        result += '@    line linestyle 3 \n'   
        result += '@line def\n'


        return result
        pass
   


    def Set_par( self, par ):
        self.__par = par # par is the Fine_parameter class object

    def Set_fontsize(self, fontsize_input = 70 ):
        self.__fontsize = fontsize_input
    
    def Get_gamma_label(self):
        width  = float( self.__I ) / 100. * 20. # linewidth max = 20
        length = self.__dim[1] - self.__dim[0]  # the y range for the page
        xrange = self.__dim[2]/1000             # the x range for the page
       
        scale_factor_x = self.__par.gamLabeLXLinear 
        scale_factor_y = self.__par.gamLabeLYLinear 
        arrow_size_y = width * 2. * length / 1000. * ( scale_factor_y )
        arrow_size_x = width * xrange * ( scale_factor_x )   
        outstr = ""
        
        #
        # the xpos, ypos, font_size, percent calculations
        # user can use fine tune it by gamLabeLXOffset and gamLabeLYOffset.
        xpos =  float(self.__xf) - arrow_size_x - \
                self.__par.gamLabeLXOffset / 10
        
        ypos =  float(self.__Ef) + arrow_size_y + \
                self.__par.gamLabeLYOffset
        
        font_size = float(self.__fontsize)/100.
        
        percent = ( float(self.__Ei) - float(self.__Ef) )/ length
        if( percent > 0.04  ):
            # we make the txt label 90 deg. 
            outstr += '@with string\n'
            outstr += '@    string on\n'
            outstr += '@    string loctype world\n'
            outstr += '@    string g0\n'
            outstr += '@    string '+ str(xpos) + ', ' + str(ypos) + ' \n'
            outstr += '@    string ' + self.__color +' \n'
            outstr += '@    string rot 90\n'
            outstr += '@    string font 6\n'
            outstr += '@    string just 5\n'  
    
            outstr += '@    string char size ' + str(font_size) + ' \n'
            outstr += '@    string def "' + str(self.__label) + '" \n'
        else:
            # if gamma line is very short, then we don't rotate txt label.
            # and reset the ypos
            ypos = float(self.__Ef)
            outstr = "" # to reset
            outstr += '@with string\n'
            outstr += '@    string on\n'
            outstr += '@    string loctype world\n'
            outstr += '@    string g0\n'
            outstr += '@    string '+ str(xpos) + ', ' + str(ypos) + ' \n'
            outstr += '@    string ' + self.__color +' \n'
            outstr += '@    string rot 0\n'
            outstr += '@    string font 6\n'
            outstr += '@    string just 5\n'  
    
            outstr += '@    string char size ' + str(font_size) + ' \n'
            outstr += '@    string def "' + str(self.__label) + '" \n'
         
         
        if( self.__gam['crossBand'] ):
            # note crossBand is determined in Cal_cross_band method. 

            
            outstr = ""  # to reset  
            
            ypos = ( float(self.__Ef) + float(self.__Ei) )/2
            ypos += self.__par.gamLabeLYOffset

            xpos = (self.__gam['xi']+ self.__gam['xf'])/2 
            xpos += self.__par.gamLabeLXOffset / 10

            outstr += '@with string\n'
            outstr += '@    string on\n'
            outstr += '@    string loctype world\n'
            outstr += '@    string g0\n'
            outstr += '@    string '+ str(xpos) + ', ' + str(ypos) + ' \n'
            outstr += '@    string ' + self.__color +' \n'
            
            if( self.__par.gamCrosstxtRot ):
                outstr += '@    string rot ' + str(self.__angle) +'\n'
            else:    
                outstr += '@    string rot 0 \n'
            

            outstr += '@    string font 6\n'
            outstr += '@    string just 2\n'  
            outstr += '@    string char size ' + str(font_size) + ' \n'
            outstr += '@    string def "' + str(self.__label) + '" \n'
             
        return outstr
    
    
    
    def Get_gamma_line(self):
        xi = self.__xi 
        xf = self.__xf
        
        width = float( self.__I ) / 100. * 20. # in xmgrace, the max value = 20.

        length   = float(self.__dim[1]) - float(self.__dim[0]) 
        # dim[1] = yup, dim[0] = ylow

        arrow_size = width * 2. * length / 1000.

        if( self.__arrow ):
            # since we use arrow, and so we have raise the end point,
            # such that the tip of arrow can on the final state.        
            # 'arrowAdjust' is set to 1 by default, this let user can fine tune it. 
            endPoint =  float( self.__Ef ) +  arrow_size * self.__par.arrowAdjust

            # cross-band is more complicated, we have to calculate the x and y
            if( self.__gam['crossBand'] ):
                xf, endPoint = \
                self.Cal_crossband_gam_angle( xf, float(self.__Ef), arrow_size )
        else:
            endPoint = float( self.__Ef )

        

        endPoint = str( endPoint )
        outstr = ""
        outstr += '@with line\n'
        outstr += '@    line on\n'
        outstr += '@    line loctype world\n'
        outstr += '@    line g0\n'
        outstr += '@    line ' + str(xi) + ',' + self.__Ei +',' \
                               + str(xf)+ ', ' + endPoint +'\n'
        outstr += ( '@    line linewidth %.2f\n' %width)
        outstr += '@    line ' + self.__color +' \n'   
        outstr += '@    line linestyle ' + self.__linestyle + ' \n'   
        if( self.__arrow): outstr += '@    line arrow 2 \n'   
        else:              outstr += '@    line arrow 0 \n'   
        #outstr += '@    line arrow length 0.5\n'
        outstr += '@    line arrow length ' + str( self.__par.arrowLength ) + '\n'
        outstr += '@    line arrow layout 1.0, 0.0\n'
        outstr += '@line def\n'
 
        # if the gamma cross the band, we would consider
        # adding an auxiliary line.
        if( self.__gam['crossBand'] ):
            outstr += self.Get_auxiliary_line()
            pass

        return outstr
        pass
    
    def Cal_crossband_gam_angle(self, xf , yf, arrow_size ):

        # step1: we need to calculate the angle of a gam line in the page.
        # we refer the page size as Xrange and Yrange.
        #
        
        Yrange = self.__dim[1] - self.__dim[0]  # the y range for the page

        bandNtotal =  self.__dim[2] / self.__par.bandwidth  
        unit = ( self.__par.bandwidth + 2*self.__par.bandspacing ) 
        Xrange =  bandNtotal * unit
        

        gamYrange = float(self.__Ei) - float(self.__Ef)
        gamXrange = abs( float(self.__xi) - float(self.__xf) )


        # since the page dimension is 800 X 600
        # for calculate the angle, we first take the ratio of gam/page ragne,
        # then transform both height and width to the same unit.
        angle_rad = math.atan2( gamYrange/Yrange, gamXrange/Xrange * 800/ 600 ) 
        if(0): print( "test angle = ", angle_rad * 180 / 3.14156 )
   
        
         

        #
        # step2: assign the change
        #

        yf += math.sin( angle_rad ) * arrow_size 
         
        # xf part needs to have more steps.
        # since arrow_size is purly in y dimension, so 
        # we need the conversion.
        xshift = math.cos( angle_rad ) * arrow_size / Yrange * 600/800 * Xrange

        
        if( self.__gam['Ei_xi'] > self.__gam['Ef_xi'] ): 
            xf += xshift
            self.__angle = int( angle_rad * 180 / 3.14156 + 0.5) # in deg
        if( self.__gam['Ei_xf'] < self.__gam['Ef_xi'] ): 
            xf -= xshift
            self.__angle = int( 360 - angle_rad * 180 / 3.14156  + 0.5)# in deg
        return xf, yf
    pass



########################################################## 


class Level( object ):
    
    def __init__( self, lvl, band_info, dim ):         
        ''' It takes a single level'''
        self.__dim = dim
        self.__lvlE = "0"
        self.__label = "0"
        self.__showlvlE = 1
        self.__textY = 0
        self.__spin = ""
        self.__color = "black"
        self.__bandN = "1"   
        self.__linestyle = "1" 
        self.__linewidth = "2"
        self.__boxW = "0"
        self.__boxColor = "black"


        if 'lvlE'  in lvl:  self.__lvlE  = lvl['lvlE']   
        if 'label' in lvl:  self.__label = lvl['label'] 
        else:  self.__label = self.__lvlE

        if 'textY' in lvl:  self.__textY = lvl['textY']       
        if 'spin'  in lvl:  self.__spin  = lvl['spin']
        if 'color' in lvl:  self.__color = lvl['color']
        if 'bandN' in lvl:  self.__bandN = lvl['bandN']
        if 'linestyle' in lvl:  self.__linestyle = lvl['linestyle']
        if 'showlvlE'  in lvl:  self.__showlvlE = int( lvl['showlvlE'] )
        if 'linewidth' in lvl:  
            self.__linewidth = float( lvl['linewidth'] ) /100 * 20.0
            self.__linewidth = str( self.__linewidth  )
        
        if 'boxW' in lvl:  self.__boxW = lvl['boxW']
        if 'boxColor' in lvl:  self.__boxColor = lvl['boxColor']

        
            
        self.__starting_bandN = band_info[0]
        self.__band_width   = band_info[1]
        self.__band_spacing = band_info[2]
        
        self.__total_bandN = 0
        self.__bandN_U = 0
        self.__bandN_L = 0
        self.__cross_band = False
        
        self.__band_xi = 0   # for txt labels
        self.__band_xf = 0

        self.__band_xi_lvl = 0  # for lvl
        self.__band_xf_lvl = 0

    def Set_fontsize(self, fontsize_input = 70 ):
        self.__fontsize = fontsize_input
             

    def Set_par(self, par):
        self.__par = par

    def Update(self, lvl ):
        lvl['xi'] = self.__band_xi_lvl
        lvl['xf'] = self.__band_xf_lvl
        pass    

    
    def Process(self):
        outStr = ""
        self.Parse_bandN()
        self.__color = self.Parse_color( self.__color )
        self.__boxColor = self.Parse_color( self.__boxColor )
        outStr += self.Get_level()
        outStr += self.Get_label_eng()
        outStr += self.Get_label_spin()
        outStr += self.Get_box()
        return outStr
        pass
    
 
 
    
    def Spin_superscript(self, spin):        
        if( spin.find('+') != -1 ):
            idx = spin.find('+')
            spin = spin[:idx] +r"\S"+ spin[idx:idx+1] + r"\N" + spin[idx+1:]
            #print( spin )
            pass
        if( spin.find('-') != -1 ):
            idx = spin.find('-')
            spin = spin[:idx] +r"\S"+ spin[idx:idx+1] + r"\N" + spin[idx+1:]
            #print( spin )
            pass
        return spin
 
 



    def Parse_bandN(self):
        """ parse the the txt we read in and 
            determine whether its band span is bigger than 1
            if >1, then we set self.__cross_band = true. """
        band_list = self.__bandN.split("_") 
        n = len( band_list )
        if( n>1 ):
            self.__bandN_L = int ( band_list[0] )
            self.__bandN_U = int ( band_list[1] )
            self.__cross_band = True        
        pass
    
 
 
 
    def Parse_color( self, color_name ):
        """ from color_name to color_idx"""
        color = color_name
        result =""        
        if color.lower() == 'black':   result = 'color 1'            
        elif color.lower() == 'red':   result = 'color 2'            
        elif color.lower() == 'green': result = 'color 3'
        elif color.lower() == 'blue':  result = 'color 4'        
        elif color.lower() == 'yellow':result = 'color 5'                    
        elif color.lower() == 'brown': result = 'color 6'            
        elif color.lower() == 'grey':  result = 'color 7'
        elif color.lower() == 'violet':result = 'color 8'        
        elif color.lower() == 'cyan':  result = 'color 9'
        elif color.lower() == 'magenta': result = 'color 10'
        elif color.lower() == 'orange':  result = 'color 11'
        elif color.lower() == 'indigo':  result = 'color 12'
        elif color.lower() == 'maroon':  result = 'color 13'
        elif color.lower() == 'turquoise': result = 'color 14'
        elif color.lower() == 'grey4':     result = 'color 15'            
        else: result =  'color 1'        
        return result  
    
 
 
 

    def Simple_case(self):
        """ the level and txt label is the same y position """
        interval = self.__band_width
        spacing  = self.__band_spacing
        unit = ( interval + 2*spacing)
        unit_away = 0        
        xpos_i = 0
        xpos_f = 0 

        # 
        # to determine the x_i and x_f position.
        #
        if (self.__cross_band ):
            #
            # for a band across multiple columns
            #
            unit_away1 = self.__bandN_L - self.__starting_bandN
            unit_away2 = self.__bandN_U - self.__starting_bandN

            xpos_i = spacing + unit*unit_away1
            xpos_f = spacing + unit*unit_away2 + interval

        else:
            #
            # the easy case
            #
            unit_away = int(self.__bandN) - self.__starting_bandN 
            xpos_i = spacing + unit*unit_away
            xpos_f = spacing + unit*unit_away + interval
       
        # for testing
        # print( "xpos_i = ", xpos_i )
        # print( "xpos_f = ", xpos_f )
        # print( "=====================")

        # for the eng and spin text label, and level
        self.__band_xi = xpos_i
        self.__band_xf = xpos_f
 
        self.__band_xi_lvl = xpos_i
        self.__band_xf_lvl = xpos_f

        ## the following is just for the output.
        outstr = ""
        outstr += '@with line\n'
        outstr += '@    line on\n'
        outstr += '@    line loctype world\n'
        outstr += '@    line g0\n'
        
        outstr += '@    line ' + str(xpos_i) + ',' + self.__lvlE +',' + str(xpos_f )+ ', ' + self.__lvlE +'\n'
        outstr += '@    line linewidth '+ self.__linewidth+'\n'
        outstr += '@    line ' + self.__color +' \n'
        outstr += '@    line linestyle ' + self.__linestyle + ' \n'   
        outstr += '@line def\n'
        
        return outstr
 




    def Wedge_case(self):
        """ the level and txt label is not the same y  """ 
        interval = self.__band_width
        spacing  = self.__band_spacing
        unit = ( interval + 2*spacing)
        unit_away = 0        
        xpos_i = 0
        xpos_f = 0 
       
        # 
        # to determine the x_i and x_f position.
        #
        if (self.__cross_band ):
            #
            # for a band across multiple columns
            #
            unit_away1 = self.__bandN_L - self.__starting_bandN
            unit_away2 = self.__bandN_U - self.__starting_bandN

            xpos_i = spacing + unit*unit_away1
            xpos_f = spacing + unit*unit_away2 + interval

        else:
            #
            # the easy case
            #
            unit_away = int(self.__bandN) - self.__starting_bandN 
            xpos_i = spacing + unit*unit_away
            xpos_f = spacing + unit*unit_away + interval
       


	    # substract 20% on each sides of a unit of bandwidth ( default )
        xpos_i_lvl = xpos_i + ( self.__par.bandwidth ) * self.__par.lvlshrink
        xpos_f_lvl = xpos_f - ( self.__par.bandwidth ) * self.__par.lvlshrink
        self.__band_xi_lvl = xpos_i_lvl
        self.__band_xf_lvl = xpos_f_lvl

        # for the eng and spin text label.
        self.__band_xi = xpos_i
        self.__band_xf = xpos_f
       
        # just a note:
	    # __band_xi_lvl is for "level" line, and __band_xi is for "txt" label

        outstr = ""
        outstr += '@with line\n'
        outstr += '@    line on\n'
        outstr += '@    line loctype world\n'
        outstr += '@    line g0\n'
        
        outstr += '@    line ' + str(xpos_i_lvl) + ','  + self.__lvlE +',' + \
                                 str(xpos_f_lvl )+ ', ' + self.__lvlE +'\n'
        outstr += '@    line linewidth '+ self.__linewidth+'\n'
        outstr += '@    line ' + self.__color +' \n'
        outstr += '@    line linestyle ' + self.__linestyle + ' \n'   
        outstr += '@line def\n'

        #--------------------------------------------------------------
        # connection line left
        outstr += '@with line\n'
        outstr += '@    line on\n'
        outstr += '@    line loctype world\n'
        outstr += '@    line g0\n'
        
        outstr += '@    line ' + str(xpos_i)  + ','  + str(self.__textY) +',' \
                               + str(xpos_i_lvl )+ ', ' + self.__lvlE +'\n'
        outstr += '@    line linewidth 2.0\n'
        outstr += '@    line ' + self.__color +' \n'
        #outstr += '@    line linestyle ' + self.__linestyle + ' \n'   
        outstr += '@line def\n'


        #--------------------------------------------------------------
        # connection line right
        outstr += '@with line\n'
        outstr += '@    line on\n'
        outstr += '@    line loctype world\n'
        outstr += '@    line g0\n' 
        outstr += '@    line ' + str(xpos_f_lvl) + ',' + self.__lvlE +',' \
                               + str(xpos_f )+ ', ' + str(self.__textY) +'\n'
        outstr += '@    line linewidth 2.0\n'
        outstr += '@    line ' + self.__color +' \n'
        #outstr += '@    line linestyle ' + self.__linestyle + ' \n'   
        outstr += '@line def\n'
        return outstr



    def Get_level(self):
        result = ""
        if( self.__textY == float(self.__lvlE) ): result = self.Simple_case()
        else: result = self.Wedge_case()         
        return result



    def Get_label_eng(self):
        
        xpos = self.__band_xi
        ypos = self.__textY  + self.__par.lvlLabeLYOffset
        # note: self.__lvlLabeLYOffset is just a minor global offset 
        # defined in freParameter.txt

        eng = ""
        font_size = float(self.__fontsize)/100.
        
        # check whether label is a number (float or integer ).
        if( self.__label.replace(".", "", 1).isdigit() ):
            # label is 100.1, 102, ...
            # set the format of level txt 
            lvlformat = ".%df" %self.__par.levelDigit
            lvleng_float = float( self.__label ) 
            eng = format( lvleng_float, lvlformat )
        else:
            # label contains text, we cannot apply format
            eng = self.__label

        
        outstr = ""
        if( self.__showlvlE ):
            outstr += '@with string\n'
            outstr += '@    string on\n'
            outstr += '@    string loctype world\n'
            outstr += '@    string g0\n'
            outstr += '@    string '+ str(xpos) + ', ' + str(ypos) + ' \n'
            outstr += '@    string ' + self.__color +' \n'
            outstr += '@    string rot 0\n'
            outstr += '@    string font 6\n'
            outstr += '@    string just 5\n'  
            # string just is for justification 
            outstr += '@    string char size ' + str(font_size) + ' \n'
            outstr += '@    string def "' + str(eng) + '" \n'
        
        return outstr
        pass


    def Get_label_spin(self):
        xpos = self.__band_xf
        ypos = self.__textY
        spin = self.__spin
        if( spin != "" ): spin = self.Spin_superscript(spin)
        font_size = float(self.__fontsize)/100.
        outstr = ""
        outstr += '@with string\n'
        outstr += '@    string on\n'
        outstr += '@    string loctype world\n'
        outstr += '@    string g0\n'
        outstr += '@    string '+ str(xpos) + ', ' + str(ypos) + ' \n'
        outstr += '@    string ' + self.__color +' \n'
        outstr += '@    string rot 0\n'
        outstr += '@    string font 6\n'
        outstr += '@    string just 4\n'  
        # jsut 12  ref point at 9 o'clock
        # just 6 , ref point at 7 o'clock. 
        outstr += '@    string char size ' + str(font_size) + ' \n'
        outstr += '@    string def "' + str(spin) + '" \n'
        
        
        return outstr
        pass
    
    def Get_box(self):
         
        # when we don't have case, just return empty string.
        if( self.__boxW == "0" ): return ""

        # set up box dimension.
        xi = self.__band_xi_lvl
        xf = self.__band_xf_lvl
        box_xi = xi
        box_xf = xi + float(self.__boxW) * (xf-xi)
        
        pageLength = self.__dim
        box_h = float(self.__linewidth)/20.0 * 125. * (pageLength/1000)
        box_yi = float(self.__lvlE)
        box_yf = float(self.__lvlE) + box_h 
       
        outstr = ""
        outstr +="@with box\n"
        outstr +="@    box on\n"
        outstr +="@    box loctype world\n"
        outstr +="@    box g0\n"
        outstr += "@    box "+ str(box_xi) + ", " + str(box_yi)\
                      + ", " + str(box_xf) + ", " + str(box_yf) +"\n"   
        outstr +="@    box linestyle 1\n"
        outstr +="@    box linewidth 1.0\n"
        outstr +="@    box color 0\n"
        outstr +="@    box fill " + self.__boxColor + "\n"
        outstr +="@    box fill pattern 9\n"
        outstr +="@box def\n"
        return outstr
        pass
 


# just for convenience...not a very important class.
class Predefine_agr( object ):
    
    def __init__(self, par, x_axis_min=0, y_axis_min=0, x_axis_max=1, y_axis_max=2000):
        self.x_axis_min = x_axis_min
        self.y_axis_min = y_axis_min
        self.x_axis_max = x_axis_max
        self.y_axis_max = y_axis_max
        self.__par = par
        pass
    
    def preSection(self):
        str1="""\
# Grace project file
#
@version 50123
"""
        str1 += "@page size " + str( self.__par.outputWidth) + ", " +\
                str( self.__par.outputHeight) + "\n"
        
        str1 += """\
@page size 800, 600
@page scroll 5%
@page inout 5%
@link page off
@map font 8 to "Courier", "Courier"
@map font 10 to "Courier-Bold", "Courier-Bold"
@map font 11 to "Courier-BoldOblique", "Courier-BoldOblique"
@map font 9 to "Courier-Oblique", "Courier-Oblique"
@map font 14 to "Courier-Regular", "Courier-Regular"
@map font 15 to "Dingbats-Regular", "Dingbats-Regular"
@map font 4 to "Helvetica", "Helvetica"
@map font 6 to "Helvetica-Bold", "Helvetica-Bold"
@map font 7 to "Helvetica-BoldOblique", "Helvetica-BoldOblique"
@map font 5 to "Helvetica-Oblique", "Helvetica-Oblique"
@map font 20 to "NimbusMonoL-Bold", "NimbusMonoL-Bold"
@map font 21 to "NimbusMonoL-BoldOblique", "NimbusMonoL-BoldOblique"
@map font 22 to "NimbusMonoL-Regular", "NimbusMonoL-Regular"
@map font 23 to "NimbusMonoL-RegularOblique", "NimbusMonoL-RegularOblique"
@map font 24 to "NimbusRomanNo9L-Medium", "NimbusRomanNo9L-Medium"
@map font 25 to "NimbusRomanNo9L-MediumItalic", "NimbusRomanNo9L-MediumItalic"
@map font 26 to "NimbusRomanNo9L-Regular", "NimbusRomanNo9L-Regular"
@map font 27 to "NimbusRomanNo9L-RegularItalic", "NimbusRomanNo9L-RegularItalic"
@map font 28 to "NimbusSansL-Bold", "NimbusSansL-Bold"
@map font 29 to "NimbusSansL-BoldCondensed", "NimbusSansL-BoldCondensed"
@map font 30 to "NimbusSansL-BoldCondensedItalic", "NimbusSansL-BoldCondensedItalic"
@map font 31 to "NimbusSansL-BoldItalic", "NimbusSansL-BoldItalic"
@map font 32 to "NimbusSansL-Regular", "NimbusSansL-Regular"
@map font 33 to "NimbusSansL-RegularCondensed", "NimbusSansL-RegularCondensed"
@map font 34 to "NimbusSansL-RegularCondensedItalic", "NimbusSansL-RegularCondensedItalic"
@map font 35 to "NimbusSansL-RegularItalic", "NimbusSansL-RegularItalic"
@map font 36 to "StandardSymbolsL-Regular", "StandardSymbolsL-Regular"
@map font 12 to "Symbol", "Symbol"
@map font 38 to "Symbol-Regular", "Symbol-Regular"
@map font 2 to "Times-Bold", "Times-Bold"
@map font 3 to "Times-BoldItalic", "Times-BoldItalic"
@map font 1 to "Times-Italic", "Times-Italic"
@map font 0 to "Times-Roman", "Times-Roman"
@map font 43 to "URWBookmanL-DemiBold", "URWBookmanL-DemiBold"
@map font 44 to "URWBookmanL-DemiBoldItalic", "URWBookmanL-DemiBoldItalic"
@map font 45 to "URWBookmanL-Light", "URWBookmanL-Light"
@map font 46 to "URWBookmanL-LightItalic", "URWBookmanL-LightItalic"
@map font 47 to "URWChanceryL-MediumItalic", "URWChanceryL-MediumItalic"
@map font 48 to "URWGothicL-Book", "URWGothicL-Book"
@map font 49 to "URWGothicL-BookOblique", "URWGothicL-BookOblique"
@map font 50 to "URWGothicL-Demi", "URWGothicL-Demi"
@map font 51 to "URWGothicL-DemiOblique", "URWGothicL-DemiOblique"
@map font 52 to "URWPalladioL-Bold", "URWPalladioL-Bold"
@map font 53 to "URWPalladioL-BoldItalic", "URWPalladioL-BoldItalic"
@map font 54 to "URWPalladioL-Italic", "URWPalladioL-Italic"
@map font 55 to "URWPalladioL-Roman", "URWPalladioL-Roman"
@map font 56 to "Utopia-Bold", "Utopia-Bold"
@map font 57 to "Utopia-BoldItalic", "Utopia-BoldItalic"
@map font 58 to "Utopia-Italic", "Utopia-Italic"
@map font 59 to "Utopia-Regular", "Utopia-Regular"
@map font 13 to "ZapfDingbats", "ZapfDingbats"
@map color 0 to (255, 255, 255), "white"
@map color 1 to (0, 0, 0), "black"
@map color 2 to (255, 0, 0), "red"
@map color 3 to (0, 255, 0), "green"
@map color 4 to (0, 0, 255), "blue"
@map color 5 to (255, 255, 0), "yellow"
@map color 6 to (188, 143, 143), "brown"
@map color 7 to (220, 220, 220), "grey"
@map color 8 to (148, 0, 211), "violet"
@map color 9 to (0, 255, 255), "cyan"
@map color 10 to (255, 0, 255), "magenta"
@map color 11 to (255, 165, 0), "orange"
@map color 12 to (114, 33, 188), "indigo"
@map color 13 to (103, 7, 72), "maroon"
@map color 14 to (64, 224, 208), "turquoise"
@map color 15 to (0, 139, 0), "green4"
@reference date 0
@date wrap off
@date wrap year 1950
@default linewidth 1.0
@default linestyle 1
@default color 1
@default pattern 1
@default font 0
@default char size 1.000000
@default symbol size 1.000000
@default sformat "%.8g"
@background color 0
@page background fill on
@timestamp off
@timestamp 0.03, 0.03
@timestamp color 1
@timestamp rot 0
@timestamp font 0
@timestamp char size 1.000000
"""
        return str1
    
    def postSection(self):
        str1="""\
@r0 off
@link r0 to g0
@r0 type above
@r0 linestyle 1
@r0 linewidth 1.0
@r0 color 1
@r0 line 0, 0, 0, 0
@r1 off
@link r1 to g0
@r1 type above
@r1 linestyle 1
@r1 linewidth 1.0
@r1 color 1
@r1 line 0, 0, 0, 0
@r2 off
@link r2 to g0
@r2 type above
@r2 linestyle 1
@r2 linewidth 1.0
@r2 color 1
@r2 line 0, 0, 0, 0
@r3 off
@link r3 to g0
@r3 type above
@r3 linestyle 1
@r3 linewidth 1.0
@r3 color 1
@r3 line 0, 0, 0, 0
@r4 off
@link r4 to g0
@r4 type above
@r4 linestyle 1
@r4 linewidth 1.0
@r4 color 1
@r4 line 0, 0, 0, 0
@g0 on
@g0 hidden false
@g0 type XY
@g0 stacked false
@g0 bar hgap 0.000000
@g0 fixedpoint off
@g0 fixedpoint type 0
@g0 fixedpoint xy 0.000000, 0.000000
@g0 fixedpoint format general general
@g0 fixedpoint prec 6, 6
@with g0
"""

        str1 += "@    world " + str(self.x_axis_min) + ", " + str(self.y_axis_min) + ", " + str(self.x_axis_max) + ", " + str(self.y_axis_max) + "\n"


        str1 += """\
@    stack world 0, 0, 0, 0
@    znorm 1
"""

        str1 += "@    view " + self.__par.cornerxmin + ", "  \
                             + self.__par.cornerymin + ", "  \
                             + self.__par.cornerxmax + ", "  \
                             + self.__par.cornerymax + "\n" 

        

        str1 += """\
@    title ""
@    title font 0
@    title size 1.500000
@    title color 1
@    subtitle ""
@    subtitle font 0
@    subtitle size 1.000000
@    subtitle color 1
@    xaxes scale Normal
@    yaxes scale Normal
@    xaxes invert off
@    yaxes invert off
@    xaxis  off
@    xaxis  type zero false
@    xaxis  offset 0.000000 , 0.000000
@    xaxis  bar off
@    xaxis  bar color 1
@    xaxis  bar linestyle 1
@    xaxis  bar linewidth 1.0
@    xaxis  label ""
@    xaxis  label layout para
@    xaxis  label place auto
@    xaxis  label char size 1.000000
@    xaxis  label font 0
@    xaxis  label color 1
@    xaxis  label place normal
@    xaxis  tick off
@    xaxis  tick major 0.2
@    xaxis  tick minor ticks 1
@    xaxis  tick default 6
@    xaxis  tick place rounded true
@    xaxis  tick in
@    xaxis  tick major size 1.000000
@    xaxis  tick major color 1
@    xaxis  tick major linewidth 1.0
@    xaxis  tick major linestyle 1
@    xaxis  tick major grid off
@    xaxis  tick minor color 1
@    xaxis  tick minor linewidth 1.0
@    xaxis  tick minor linestyle 1
@    xaxis  tick minor grid off
@    xaxis  tick minor size 0.500000
@    xaxis  ticklabel off
@    xaxis  ticklabel format general
@    xaxis  ticklabel prec 5
@    xaxis  ticklabel formula ""
@    xaxis  ticklabel append ""
@    xaxis  ticklabel prepend ""
@    xaxis  ticklabel angle 0
@    xaxis  ticklabel skip 0
@    xaxis  ticklabel stagger 0
@    xaxis  ticklabel place normal
@    xaxis  ticklabel offset auto
@    xaxis  ticklabel offset 0.000000 , 0.010000
@    xaxis  ticklabel start type auto
@    xaxis  ticklabel start 0.000000
@    xaxis  ticklabel stop type auto
@    xaxis  ticklabel stop 0.000000
@    xaxis  ticklabel char size 1.000000
@    xaxis  ticklabel font 0
@    xaxis  ticklabel color 1
@    xaxis  tick place both
@    xaxis  tick spec type none
@    yaxis  on
@    yaxis  type zero false
@    yaxis  offset 0.000000 , 0.000000
@    yaxis  bar off
@    yaxis  bar color 1
@    yaxis  bar linestyle 1
@    yaxis  bar linewidth 1.0
@    yaxis  label ""
@    yaxis  label layout para
@    yaxis  label place auto
@    yaxis  label char size 0.850000
@    yaxis  label font 0
@    yaxis  label color 1
@    yaxis  label place normal
@    yaxis  tick off
@    yaxis  tick major 500
@    yaxis  tick minor ticks 1
@    yaxis  tick default 6
@    yaxis  tick place rounded true
@    yaxis  tick in
@    yaxis  tick major size 0.700000
@    yaxis  tick major color 1
@    yaxis  tick major linewidth 1.0
@    yaxis  tick major linestyle 1
@    yaxis  tick major grid off
@    yaxis  tick minor color 1
@    yaxis  tick minor linewidth 1.0
@    yaxis  tick minor linestyle 1
@    yaxis  tick minor grid off
@    yaxis  tick minor size 0.500000
@    yaxis  ticklabel off
@    yaxis  ticklabel format general
@    yaxis  ticklabel prec 5
@    yaxis  ticklabel formula ""
@    yaxis  ticklabel append ""
@    yaxis  ticklabel prepend ""
@    yaxis  ticklabel angle 0
@    yaxis  ticklabel skip 0
@    yaxis  ticklabel stagger 0
@    yaxis  ticklabel place normal
@    yaxis  ticklabel offset auto
@    yaxis  ticklabel offset 0.000000 , 0.010000
@    yaxis  ticklabel start type auto
@    yaxis  ticklabel start 0.000000
@    yaxis  ticklabel stop type auto
@    yaxis  ticklabel stop 0.000000
@    yaxis  ticklabel char size 0.700000
@    yaxis  ticklabel font 0
@    yaxis  ticklabel color 1
@    yaxis  tick place normal
@    yaxis  tick spec type none
@    altxaxis  off
@    altyaxis  off
@    legend on
@    legend loctype view
@    legend 0.85, 0.8
@    legend box color 1
@    legend box pattern 1
@    legend box linewidth 1.0
@    legend box linestyle 1
@    legend box fill color 0
@    legend box fill pattern 1
@    legend font 0
@    legend char size 1.000000
@    legend color 1
@    legend length 4
@    legend vgap 1
@    legend hgap 1
@    legend invert false
@    frame type 0
@    frame linestyle 0
@    frame linewidth 1.0
@    frame color 0
@    frame pattern 0
@    frame background color 0
@    frame background pattern 0
        """        
        return str1





