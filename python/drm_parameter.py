# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 21:12:46 2016

@author: flo
"""
import numpy

# Sammlung aller Parameter für DRM
# MODE INDEX
#  A     1
#  B     2
#  C     3
#  D     4
modes  = ['Nicht erkannt', 'A', 'B', 'C', 'D']

# OFDM Symbole
prefix_length     = [  0,  128,  256, 256, 352]
symbol_length     = [  0, 1280, 1280, 960, 800]
num_subcarries    = [  0,    0,    0,   0,   0]
symbols_per_frame = [  0,   15,   15,  20,  24] 



###########################################
# Unterträgernutzung, Spectrumoccupancy
###########################################
msc_qam_cells     = [[], #kein mode
                     [], # a
                     [2900, 3330, 6153, 7013, 12747, 14323], # b
                     [],
                     []]
msc_qam_cells_loss= [[], #kein mode
                     [], # a
                     [2,0,0,2,0,1], # b
                     [],
                     []]
msc_dummy_symbols = [1+1j, 1-1j]
                     
                     
###########################################
# Unterträgernutzung, Spectrumoccupancy
###########################################
k_min_A    = [    2,    2, -102, -114,  -98, -110 ]
k_max_A    = [  102,  114,  102,  114,  314,  350 ]

k_min_B    = [    1,    1,  -91, -103,  -87,  -99 ]
k_max_B    = [   91,  103,   91,  103,  279,  311 ]

k_min_C    = [    0,    0,    0,    0,    0,    0 ]
k_max_C    = [    0,    0,    0,    0,    0,    0 ]

k_min_D    = [    0,    0,    0,    0,    0,    0 ]
k_max_D    = [    0,    0,    0,    0,    0,    0 ]
                                            
unused_subc = [[],
               [-1,0,1],#A
               [0],#B
               [0],#C
               [0],#D
               [],#E
               ]

###########################################
# Frequenzreferenzen
###########################################
# alle Modes nutzen die selben Frequenzen und die Frequenzsync ist unabhängig vom Mode
# 48 kHz, 1024 FFT
# Unterträger
freq_ref_sc  = [ 16,  48,  64]
# Amplitude
freq_ref_amp = numpy.sqrt(2)
# Phasenwerte
freq_ref_vk  = [331, 651, 555]
freq_ref_pha = numpy.multiply( (2 * numpy.pi / 1024), freq_ref_vk )
# Referenz
freq_ref     = numpy.multiply( freq_ref_amp, numpy.exp(1j * freq_ref_pha) )



###########################################
# Zeitreferenzen
###########################################
time_ref_sc  = [ [0],
                 [0],
                 [14,  16,  18,  20,  24,  26, 32,  36,  42,  44,  48,  49,  50,  54,  56,  62,  64,  66,  68],
                 [0],
                 [0] ]
time_ref_amp = numpy.sqrt(2)
time_ref_vk  = [ [0], 
                 [0],
                 [304, 331, 108, 620, 192, 704, 44, 432, 588, 844, 651, 651, 651, 460, 460, 944, 555, 940, 428],
                 [0],
                 [0] ]


###########################################
# Gainreferenzenz
###########################################
# bis jetzt nur MODE B implementiert
                 
        
time_ref_amp            = numpy.sqrt(2) #1  #numpy.sqrt(2) # sollte numpy.sqrt(2), scheint im sender 1
time_ref_amp_boosted    = 2#numpy.sqrt(2) #2
time_ref_boosted_A      = [ [0], 
                            [0],
                            [0],
                            [0],
                            [0] 
                            ]
time_ref_boosted_B      = [ [1,3,89,91], 
                            [1,3,101,103],
                            [-91, -89, 89, 91],
                            [-103,-101,101, 103],
                            [-87, -85, 277, 279],
                            [-99,-97, 309, 311] 
                            ]
time_ref_boosted_C      = [ [0], 
                            [0],
                            [0],
                            [0],
                            [0] 
                            ]
time_ref_boosted_D      = [ [0], 
                            [0],
                            [0],
                            [0],
                            [0] 
                            ]
                            
frame_len       = [0,0,15,0,0,0]

super_frame_len = [0,0,3 ,0,0,0]
                            
                            
def gain_pos_A(k_min, k_max, symbol):
    k = []    
    for p in range(k_min-20, k_max + 20):
        new_val =2 + 4 * (symbol%5) + 20 * p
        if k_min <= new_val and k_max >= new_val:
            k.append(new_val)
    return k
def gain_pos_B(k_min, k_max, symbol):
    k = []
    limit = numpy.max( [numpy.abs(k_min), numpy.abs(k_max)] )
    for p in range(-limit-6, limit + 6):
        new_val =1 + 2 * (symbol%3) + 6 * p
        if k_min <= new_val and k_max >= new_val:
            k.append(new_val)
    return k
def gain_pos_C(k_min, k_max, symbol):
    k = []    
    for p in range(k_min, k_max + 1):
        new_val =1 + 2 * (symbol%2) + 4 * p
        if k_min <= new_val and k_max >= new_val:
            k.append(new_val)
    return k
def gain_pos_D(k_min, k_max, symbol):
    k = []    
    for p in range(k_min, k_max + 1):
        k.append(1 + 1 * (symbol%3) + 3 * p)
    return k
def gain_pos_E(k_min, k_max, symbol):
    k = []    
    for p in range(k_min, k_max + 1):
        k.append(2 + 4 * (symbol%4) + 16 * p)
    return k



def get_gain_pha( mode, symbol, k ):
    ''' Gibt die Phase zum jeweiligen Referenzpunkt aus '''
    mode_a = [4.,5,2]
    mode_b = [2.,3,1]
    mode_c = [2.,2,1]
    mode_d = [1.,3,1]
    mode_e = [4.,4,2]
    params = { 0:0, 
              1:mode_a, 
              2:mode_b, 
              3:mode_c, 
              4:mode_d,
              5:mode_e
              }
    
    n = int( symbol % params[mode][1] )
    m = int( numpy.floor(symbol / params[mode][1]) )
    
    p = 0.0
    p = k - params[mode][2]-n* params[mode][0]
    p = p / (params[mode][0] * params[mode][1])
    
    w1024b = [ [512,  0, 512,   0, 512],
               [0  ,512,   0, 512, 0],
               [512,  0, 512,   0, 512]
             ]
    z256b  = [ [  0, 57, 164,  64,  12],
               [168,255, 161, 106, 118],
               [ 25,232, 132, 233,  38] 
             ]
    q1024b = 12
    if mode == 2:
        vk = ( 4 * z256b[n][m] + p * w1024b[n][m] + p*p*(1+symbol)*q1024b )%1024
    else:
        vk = 0
        print('nicht implementiert')
        
    return vk

def get_gain_amp( mode, k, rm=0):
    boost_func = { 0:0,
                   1:time_ref_boosted_A,
                   2:time_ref_boosted_B,
                   3:time_ref_boosted_C,
                   4:time_ref_boosted_D
                   }
                
    
    for ref_val in boost_func[mode][rm]:
        if k == ref_val:
            return time_ref_amp_boosted
    return time_ref_amp
                            
    
def get_k_min(mode, rm = 0, boosted = 1):
    ''' Gibt k_min zurück, wenn boosted = 0 ohne die geboosteten Randwerte '''
    k_min_a = [1,1, -91, -103, -87, -99]
    k_min_b = [1,1, -91, -103, -87, -99]
    
    k_min = { 0:0, 
              1:k_min_a,
              2:k_min_b}
              
    boost_func = { 0:0,
                   1:time_ref_boosted_A,
                   2:time_ref_boosted_B,
                   3:time_ref_boosted_C,
                   4:time_ref_boosted_D
                   }
                   
    if boosted == 0:
        k_min = numpy.min(boost_func[mode][rm]) + 1 + 6 # von mode abhängig fixen
    else:
        k_min = numpy.min(k_min[mode][rm])
    return  k_min
    
def get_k_max(mode, rm = 0, boosted = 1):
    ''' Gibt k_max zurück, wenn boosted = 0 ohne die geboosteten Randwerte '''
    k_max_a = [102 , 114, 102, 114, 314, 350]
    k_max_b = [ 91 , 103,  91, 103, 279, 311]
    
    k_max = { 0:0, 
              1:k_max_a,
              2:k_max_b}
              
    boost_func = { 0:0,
                   1:time_ref_boosted_A,
                   2:time_ref_boosted_B,
                   3:time_ref_boosted_C,
                   4:time_ref_boosted_D
                   }
                   
    if boosted == 0:
        k_max = numpy.max(boost_func[mode][rm]) - 1 - 6 # von mode abhängig fixen
    else:
        k_max = numpy.max(k_max[mode][rm])
    return  k_max
    

def get_gain_ref( mode, rm = 0, rm_valid = 0):
    # funktionen definieren
    pos_func = { 0:0, 
                 1:gain_pos_A,
                 2:gain_pos_B,
                 3:gain_pos_C,
                 4:gain_pos_D,
                 5:gain_pos_E 
                 }
                   
    m_k_min = get_k_min(mode, rm, rm_valid)
    m_k_max = get_k_max(mode, rm, rm_valid)
    
    num_sc  = numpy.abs(m_k_max - m_k_min) + 1
    num_sym = symbols_per_frame[mode]
    
    ref = numpy.zeros( (num_sym, num_sc), dtype=numpy.complex64 )
    
    for n_sym in range(0, num_sym):
        positions = pos_func[mode](m_k_min, m_k_max, n_sym)
        
        for n_k in positions:
            ref[n_sym][n_k-m_k_min] = get_gain_amp(mode, n_k, rm) * numpy.exp( 2j*numpy.pi* get_gain_pha(mode,n_sym, n_k) / 1024) 
    
    return ref 
    
    
    
    

###########################################
# FFT Parameter für richtigen Unterträgerabstand
###########################################
# Unterträgerabstand = 1/TU (TS A: 24ms B: 21.33 C: 14.66ms D: 9.33ms)
# Unterträgerabstand =  A: 41.66 B: 46.875 C: 68.182 D: 107.143 (werte gerundet)
# fs = 1024 * Uabstand
fft_len      = [ [0],
                 [1024],
                 [1024],
                 [0],
                 [0] ]
sample_rate  = [ [0],
                 [42659.84],
                 [48000],
                 [0],
                 [0] ]


###########################################
# FAC Parameter
###########################################
fac_b       = [  []  #1
                ,[13, 25, 43, 55, 67]  #2
                ,[15, 27, 45, 57, 69]  #3
                ,[17, 29, 47, 59, 71]  #4
                ,[19, 31, 49, 61, 73]  #5
                ,[9, 21, 33, 51, 63, 75]  #6
                ,[11, 23, 35, 53, 65, 77]  #7
                ,[13, 25, 37, 55, 67, 79]  #8
                ,[15, 27, 39, 57, 69, 81]  #9
                ,[17, 29, 41, 59, 71, 83]  #10
                ,[19, 31, 43, 61, 73]  #11
                ,[21, 33, 45, 63, 75]  #12
                ,[23, 35, 47, 65, 77]  #13
                ,[]  #14
                ,[] ] #15
                

###########################################
# Funktionen
###########################################
def get_time_ref(mode):
    if mode == 2:
        return 1
    else:
        return 0
    
def get_freq_ref(mode):
    return 0
    
#def get_gain_ref(mode):
#    if mode == 2:
#        return 1
#    else:
#        return 0

def get_eq_range_fac(mode):
    return 0
    