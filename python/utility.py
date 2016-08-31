# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 13:44:13 2016

@author: flo
"""
import numpy
import time

def bit_list_to_int( list_in ):
    '''Wandelt eine Liste voller einsen und Nullen in die dazugehörige Ganzzahl um
    
        
    '''
    out = 0
    for x in list_in:
        out = ( out << 1 ) | x
    return out
    
    
def frame_interpolator( diff_frame, ref_frame ):
    n_syms = len( diff_frame )
    n_subc = len( diff_frame[0] )
    
    # über alle symbole im frame interpolieren
    ref_sc =  numpy.zeros(n_subc)
    
#    print('REF')
#    numpy.set_printoptions(precision=2, suppress=True)
#    for test_p in range(0,7):
#        print((diff_frame[test_p][0:6]))       
    
    for k in range(0, n_subc):
        start = 0
        ende  = n_syms - 1
        s1    = -1
        s2    = -1
        s2_p  = 0
        s1_p  = 0
        d_diff = 0.0j
        for j in range(0, n_syms):
            if ref_frame[j][k] != 0:
                s2 = s1
                s1 = diff_frame[j][k]
                s2_p = s1_p
                s1_p = j
                if s1 != -1 and s2 != -1:
                    ref_sc[k]=1
                    #interpoliere sobald 2 symbole bekannt sind
                    d_diff = (s1 - s2)
                    d_diff = d_diff / (s1_p - s2_p )
                    n = 1
                    for int_pos in range (s2_p+1, s1_p):
                        diff_frame[int_pos][k] = diff_frame[s2_p][k] + d_diff * n
                        n+=1
                    
                    # rückwärtsinterpolieren falls noch werte fehlen
                    if start == 0 and s2_p != 0:
                        n = 1
                        for int_ps in range(0, s2_p):
                            diff_frame[s2_p - int_ps - 1][k] = diff_frame[s2_p][k] - d_diff * n
                            n+=1
                            start = s1_p
                    
                    if start == 0 and s2_p == 0:
                        start = -1
                            
            # vorwärtsinterpolieren falls Ende erreicht wird
            # und schon 2 symbole gefunden wurden
            if j == ende and j != s1_p and s1 != -1 and s2 != -1:
                n = 1
                for int_pos in range(s1_p+1, ende + 1):
                    diff_frame[int_pos][k] = diff_frame[s1_p][k] + d_diff * n
                    n+=1
                    
#
#    print('Part 1')
#    for test_p in range(0,7):
#        print((diff_frame[test_p][0:6]))               
    # Nächste Richtung durchinterpolieren           
    for j in range(0, n_syms):    
        start = 0
        ende  = n_subc - 1
        s1    = -1
        s2    = -1
        s2_p  = 0
        s1_p  = 0
        d_diff = 0.0j      
        for k in range(0, n_subc):
            if ref_sc[k] != 0:
                s2 = s1
                s1 = diff_frame[j][k]
                s2_p = s1_p
                s1_p = k
                if s1 != -1 and s2 != -1:
                    #interpoliere sobald 2 symbole bekannt sind
                    d_diff = (s1 - s2)
                    d_diff = d_diff / (s1_p - s2_p )
                    n = 1

                    for int_pos in range (s2_p+1, s1_p):
                        diff_frame[j][int_pos] = diff_frame[j][s2_p] + d_diff * n
                        n+=1
                    # rückwärtsinterpolieren falls noch werte fehlen
                    if start == 0 and s2_p != 0:
                        n = 1
                        for int_ps in range(0, s2_p):
                            diff_frame[j][s2_p - int_ps - 1] = diff_frame[j][s2_p] - d_diff * n
                            n+=1
                            start = s1_p
                    
                    if start == 0 and s2_p == 0:
                        start = -1
            # vorwärtsinterpolieren falls Ende erreicht wird
            # und schon 2 symbole gefunden wurden
            if k == ende and k != s1_p and s1 != -1 and s2 != -1:
                n = 1
                for int_pos in range(s1_p+1, ende + 1):
                    diff_frame[j][int_pos] = diff_frame[j][s1_p] + d_diff * n
                    n+=1

#    print('Part 2')        
#    for test_p in range(0,7):
#        print((diff_frame[test_p][0:6]))
#    print('Part 2 amp')        
#    for test_p in range(0,7):
#        print(numpy.abs(diff_frame[test_p][0:6]))
#    print('Part 2 pha')        
#    for test_p in range(0,7):
#        print(numpy.angle(diff_frame[test_p][0:6]) / (numpy.pi * 2) ) 
#    return ref_sc
                    
                        

                        
                    
                    
                    