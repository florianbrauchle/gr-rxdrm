# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 17:10:53 2016

@author: flo
"""
import numpy


import utility


# Ablauf
# Cell Interleaving (only MSC)
# Mapping 
# Bit Interleaving
# Coding
# Partioning of Information (Multilevel coding)
# Energy Dispersal
# Transport Multiplex


#def trans_mult():
#    l_fac = 72 # Bits per Block
#    n_fac = 65 # ofdm cells per fac
#    p_max = 1
#    L_fac = l2
#    N_fac = N2
#    # onle eep and sm
#    l_mux = l2
#    s
#    return

#Energy Dispersal
# das Schieberegister wird für jeden FAC block zurück gesetzt
def scrambler( bits_in, shift_register_init = [1]*9 ):
    shift_register = list(shift_register_init)
    len_reg = len( shift_register )
    
    #     
    bits_out = [0] * len(bits_in)   
    
    n = 0
    for bit in bits_in:
        # Schieberegister und Berechnung der Pseudo Random Bit Sequence        
        prbs = (shift_register[0] + shift_register[4]) % 2
        shift_register[0:len_reg - 1] = shift_register[1:len_reg]
        shift_register[len_reg-1] = prbs
        
        bits_out[n] = (bit + prbs) % 2
        n += 1
        
    return bits_out


# Viterbi decoder
class viterbi:
    p0 = [1,0,1,1,0,1,1]
    p1 = [1,1,1,1,0,0,1]
    p2 = [1,1,0,0,1,0,1]
    p3 = p0
    p4 = p1
    p5 = p2
    init_state = [0,0,0,0,0,0]
    
    states  = [ [0,0,0,0,0,0],[0,0,0,0,0,1],[0,0,0,0,1,0],[0,0,0,0,1,1],[0,0,0,1,0,0],[0,0,0,1,0,1],[0,0,0,1,1,0],[0,0,0,1,1,1], #7
                
                [0,0,1,0,0,0],[0,0,1,0,0,1],[0,0,1,0,1,0],[0,0,1,0,1,1],[0,0,1,1,0,0],[0,0,1,1,0,1],[0,0,1,1,1,0],[0,0,1,1,1,1], #15
                
                [0,1,0,0,0,0],[0,1,0,0,0,1],[0,1,0,0,1,0],[0,1,0,0,1,1],[0,1,0,1,0,0],[0,1,0,1,0,1],[0,1,0,1,1,0],[0,1,0,1,1,1], #23
                [0,1,1,0,0,0],[0,1,1,0,0,1],[0,1,1,0,1,0],[0,1,1,0,1,1],[0,1,1,1,0,0],[0,1,1,1,0,1],[0,1,1,1,1,0],[0,1,1,1,1,1], #31
                
                [1,0,0,0,0,0],[1,0,0,0,0,1],[1,0,0,0,1,0],[1,0,0,0,1,1],[1,0,0,1,0,0],[1,0,0,1,0,1],[1,0,0,1,1,0],[1,0,0,1,1,1], #39
                [1,0,1,0,0,0],[1,0,1,0,0,1],[1,0,1,0,1,0],[1,0,1,0,1,1],[1,0,1,1,0,0],[1,0,1,1,0,1],[1,0,1,1,1,0],[1,0,1,1,1,1], #47
                [1,1,0,0,0,0],[1,1,0,0,0,1],[1,1,0,0,1,0],[1,1,0,0,1,1],[1,1,0,1,0,0],[1,1,0,1,0,1],[1,1,0,1,1,0],[1,1,0,1,1,1], #55
                [1,1,1,0,0,0],[1,1,1,0,0,1],[1,1,1,0,1,0],[1,1,1,0,1,1],[1,1,1,1,0,0],[1,1,1,1,0,1],[1,1,1,1,1,0],[1,1,1,1,1,1],]#63
                
    trans_0 =   [ 0,  0,  1,  1,  2,  2,  3,  3, #7
                  4,  4,  5,  5,  6,  6,  7,  7, #15
                  8,  8,  9,  9, 10, 10, 11, 11, #23
                 12, 12, 13, 13, 14, 14, 15, 15, #31
                 16, 16, 17, 17, 18, 18, 19, 19, #39
                 20, 20, 21, 21, 22, 22, 23, 23, #47
                 24, 24, 25, 25, 26, 26, 27, 27, #89
                 28, 28, 29, 29, 30, 30, 31, 31,]#63
                 
    trans_1 =   numpy.add(trans_0, 32)
    trans_prob = numpy.zeros((64,64))
    
    
    # Zustandstransmissionsmatrix
    for n in range(0,64):
        trans_prob[n][trans_0[n]] = 0.5
        trans_prob[n][trans_1[n]] = 0.5

    
    # Startzustands wahrscheinlichkeiten    
    a_pi    = numpy.zeros(64)
    a_pi[0] = 1
                 
                 
    # Variablen
    state = [0,0,0,0,0,0]
    def init(self, p_mat):
        self.state = self.init_state
        
    def calc_error(self, state, bits_rec, bit_val ):
        ''' Berechnet die Hemmingdistanz für jedes Empfangene Symbol'''
        # Berechne Hemmingdistanz
        ref_bits = [0] * 6
        ref_bits[0] = numpy.sum(numpy.multiply(self.p0, [bit_val] + self.states[state])) % 2
        ref_bits[1] = numpy.sum(numpy.multiply(self.p1, [bit_val] + self.states[state])) % 2
        ref_bits[2] = numpy.sum(numpy.multiply(self.p2, [bit_val] + self.states[state])) % 2
#        ref_bits[3] = numpy.sum(numpy.multiply(self.p3, [bit_val] + [self.states[state]])) % 2
#        ref_bits[4] = numpy.sum(numpy.multiply(self.p4, [bit_val] + [self.states[state]])) % 2
#        ref_bits[5] = numpy.sum(numpy.multiply(self.p5, [bit_val] + [self.states[state]])) % 2
        ref_bits[3] = ref_bits[0]
        ref_bits[4] = ref_bits[1]
        ref_bits[5] = ref_bits[2]
        error = 0
        for n in range(0,6):
            if bits_rec[n] != 0: # Punktierte Bits = 0, sonst +-1
                error += numpy.abs( bits_rec[n] - ( (ref_bits[n] - 0.5) * 2 ) )
        return error/2 
        
    def calc_error_dbug(self, state, bits_rec, bit_val ):
        ''' Berechnet die Hemmingdistanz für jedes Empfangene Symbol'''
        # Berechne Hemmingdistanz
        ref_bits = [0] * 6
        ref_bits[0] = numpy.sum(numpy.multiply(self.p0, [bit_val] + self.states[state])) % 2
        ref_bits[1] = numpy.sum(numpy.multiply(self.p1, [bit_val] + self.states[state])) % 2
        ref_bits[2] = numpy.sum(numpy.multiply(self.p2, [bit_val] + self.states[state])) % 2
#        ref_bits[3] = numpy.sum(numpy.multiply(self.p3, [bit_val] + [self.states[state]])) % 2
#        ref_bits[4] = numpy.sum(numpy.multiply(self.p4, [bit_val] + [self.states[state]])) % 2
#        ref_bits[5] = numpy.sum(numpy.multiply(self.p5, [bit_val] + [self.states[state]])) % 2
        ref_bits[3] = ref_bits[0]
        ref_bits[4] = ref_bits[1]
        ref_bits[5] = ref_bits[2]
        bits_rec2 = [int((x/2)+1) for x in bits_rec]
        print(' ' + str(bit_val) + ': '),
        for i in range(0, len(bits_rec)):
            if bits_rec[i] != 0:
                print( str(ref_bits[i]) + '(' + str(bits_rec2[i]) + ')' ),
        print(' (rx value)')

    
    def decode( self, bits_in, debug = 0 ):
        len_trellis        = (len(bits_in)/6) #+1
        state_prob         = [1] + [0] * 63
        prev_state         = numpy.zeros( (64, len_trellis +1 ) )
        acc_err    = numpy.empty( (64, len_trellis +1 ) )
        acc_err[:] = numpy.nan
        acc_err[0][0] = 0   
        
        for m in range (0, len_trellis):
            #print(self.state_prop)
            #print( bits_in[0+m*6:6+m*6] )
            
                
            for n in range(0,64):
                #print( state_prob[n])
                if state_prob[n] != 0:
                    b_0 = self.calc_error(n,bits_in[0+m*6:6+m*6], 0)
                    b_1 = self.calc_error(n,bits_in[0+m*6:6+m*6], 1)
                    
                    next_state = self.trans_0[n]                        
                    #if debug:
                        #if acc_err[n][m] == 0:
                            #print( str(int(m)) + ' State ' + str(n) + ' 0:' + str( int(b_0) ) + ' 1:' + str(int(b_1) )  )
                            #self.calc_error_dbug(n,bits_in[0+m*6:6+m*6], 0)
                            #self.calc_error_dbug(n,bits_in[0+m*6:6+m*6], 1)
                    if (acc_err[next_state][m+1] > acc_err[n][m] + b_0 ) or numpy.isnan(acc_err[next_state][m+1]):
                        if numpy.isnan(acc_err[n][m]):
                            acc_err[next_state][m+1] = b_0
                        else:
                            acc_err[next_state][m+1] = acc_err[n][m] + b_0
                        prev_state[next_state][m+1] = n
                    
                    next_state = self.trans_1[n]
                    if (acc_err[next_state][m+1] > acc_err[n][m] + b_1 ) or numpy.isnan(acc_err[next_state][m+1]):
                        if numpy.isnan(acc_err[n][m]):
                            acc_err[next_state][m+1] = b_1
                        else:
                            acc_err[next_state][m+1] = acc_err[n][m] + b_1
                        prev_state[next_state][m+1] = n
            state_prob = numpy.dot(state_prob, self.trans_prob)
            
        # Pfad mit kleinstem Fehler suchen        
        #print( [x[len_trellis] for x in acc_err] )        
        best_res   = numpy.nanargmin( [x[len_trellis] for x in acc_err] )
        if debug:
            print( 'Bester Pfad : ' + str(best_res) + ' Fehler: ' + str(acc_err[best_res][len_trellis])  )
      
        #Traceback
        bits_out   = numpy.zeros(len_trellis)
        
        state      = best_res
        #print( 'Trace: ' + str(state))
        for n in range(0, len_trellis):
            #print(self.trans_0[int(prev_state[state][int(len_trellis-n)])])
            if self.trans_0[int(prev_state[int(state)][int(len_trellis-n)])] == state:
                bits_out[len_trellis-1-n] = int(0)
            else:
                bits_out[len_trellis-1-n] = int(1)
            state = prev_state[int(state)][int(len_trellis-n)]
            #print( 'Trace: ' + str(state))
        return bits_out
                              
    

    
# Bit Reverse Interleaving 
def bit_deinterleaving( bits_in, t = 21 ):
    # 4QAM
    t_0  = t
    #p   = [0,1,2] # for FAC p = 0
    xi  = len(bits_in)
    s   = numpy.power( 2, numpy.ceil( numpy.log2(xi) ) )
    q   = s/4 - 1
    
    cap_pi_0        = 0
    cap_pi_0_old    = 0
    
    bits_out        = [0] * xi
    
    for i in range(0, xi):
        if i == 0:
            cap_pi_0 = 0
        else:
            cap_pi_0 =  (t_0 * cap_pi_0_old + q) % s
            while cap_pi_0 >= xi:
                cap_pi_0 = (t_0 * cap_pi_0 + q) % s
        cap_pi_0_old = cap_pi_0
        #print(cap_pi_0)
        cap_pi_0 = int( cap_pi_0 )
        bits_out[cap_pi_0] = bits_in[i]
        #bits_out[i] = bits_in[cap_pi_0]

    return bits_out
    

   
   
   # Multilevel Coding für FAC nur 1 Level, da 4 QAM
   

# Rall 0.6 R0 3/5
# Puncturing Pattern:
# 1 1 1
# 1 0 1
# 0 0 0
# 0 0 0
# fügt die beim Punktieren verlorenen Bits wieder ein (mit Wert null)
# und setzt die bitwerte zu -1(0) und 1 (1)
def dec_reform(bits_in, punctering_mode=0):
    punc_pat = [[1,1,0,0,0,0],[1,0,0,0,0,0],[1,1,0,0,0,0]] 
    
    m = 0
    n = 0
    len_out = len(bits_in) * 18 / 5 
    #print(len_out)

    # 3/5 mit aufgefülltem puncturing wird zu 1/4, also 3/12
    # 3/5 mit aufgefülltem puncturing wird zu 1/6, also 3/12 neuer Standard
    bits_out = [0] * len_out    
    #print( len( punc_pat[1]) )
    #print( len( punc_pat) )
    while m < len( bits_in ):
        #print( (n/len(punc_pat[0]))%len(punc_pat) )
        for mask in punc_pat[(n/len(punc_pat[0]))%len(punc_pat)]:
            if mask == 0:  
                bits_out[n] = 0
            else:
                #print('in' + str(m) + ' out' + str(n) )
                bits_out[n] = int( ( bits_in[m] - 0.5 ) * 2 )
                m += 1
            n += 1
            
    return bits_out
    
# Demod
def qam_slicer(sym_in, qam_level=4):
    bits_out = [0] * int( numpy.log2(qam_level) * len(sym_in) )
    
    for sym in range(0, len(sym_in)):
        if numpy.imag( sym_in[sym] ) < 0:
            bits_out[1 + 2*sym] = 1
        else:
            bits_out[1 + 2*sym] = 0
            
        if numpy.real( sym_in[sym] ) < 0:
            bits_out[0 + 2*sym] = 1
        else:
            bits_out[0 + 2*sym] = 0
    return bits_out

    
def crc_check(bits_in):
    # fac : x8 x4 x3 x2 1 
    shift_reg = numpy.ones(8)
    shift_reg_old = shift_reg
    for i in range( 0, len(bits_in) ):
        shift_reg_old = list(shift_reg)
        bit_add = (bits_in[i] + shift_reg_old[0])%2
        shift_reg[7]  = bit_add
        shift_reg[6]  = shift_reg_old[7]
        shift_reg[5]  = (shift_reg_old[6] + bit_add)%2
        shift_reg[4]  = (shift_reg_old[5] + bit_add)%2
        shift_reg[3]  = (shift_reg_old[4] + bit_add)%2
        shift_reg[2]  = shift_reg_old[3]
        shift_reg[1]  = shift_reg_old[2]
        shift_reg[0]  = shift_reg_old[1]
    
    if numpy.sum(shift_reg) == 0:
        return 1
    else:
        return 0
        
class fac_data:
    # CHANNEL PARAMETERS
    # Base Enhancement Flag
    base_flag              = 0
    # Identity
    identity               = 0
    # RM Flag
    rm_flag                = 0
    # Spectrum occupancy
    spectrum_occupancy     = 0
    # INterleaver depth flag 
    interleaver_depth      = 0 
    # MSC mode
    msc_mode               = 0
    # SDC mode
    sdc_mode               = 0
    sdc_mode_qam           = 0
    sdc_mode_cr            = 0
    # Number of Services
    audio_services         = 0
    data_services          = 0
    # Reconfiguraiton index
    reconfiguration_index  = 0
    # Toggle Flag
    toggle_flag            = 0
    # rfu
    rfu                    = 0
    
    # SERVICE PARAMETERS
    #Service identifier
    service_identifier     = 0
    # Short Id
    short_id               = 0
    # Audio CA indication
    audio_ca               = 0
    # Language
    language               = 0
    # Audio/Data Flag
    ad_flag                = 0
    # Service Descriptor
    service_desc           = 0
    # Data CA indication
    data_ca                = 0
    # rfa
    rfa                    = 0
    
    # Hilfsvariablen
    dic_so = {0:4.5,1:5,2:9,3:10,4:18,5:20}
    dic_interleaver_0   = {0: 2000, 1:400 }
    dic_interleaver_1   = {0: 600 , 1: 0  }
    dic_qam_0           = {0: 16, 1: 4}
    dic_qam_1           = {0:  4, 1: 4}
    dic_cr_0            = {0: 0.5, 1:0.5}
    dic_cr_1            = {0: 0.5, 1:0.25}
    dic_audio_service   = {0:4,1:0,2:0,3:0,4:1,5:1,6:1,7:1,8:2,9:2,10:2,11:0,12:3,13:3,14:0,15:0}
    dic_data_service    = {0:0,1:1,2:2,3:3,4:0,5:1,6:2,7:3,8:0,9:1,10:2,11:0,12:0,13:1,14:0,15:4}
    dic_language        = {0 :'not specified',
                           1 :'Arabic',
                           2 :'Bengali',
                           3 :'Chinese(Mandarin)',
                           4 :'Dutch',
                           5 :'English',
                           6 :'French',
                           7 :'German',
                           8 :'Hindi',
                           9 :'Japanese',
                           10:'Javanese',
                           11:'Korean',
                           12:'Portuguese',
                           13:'Russian',
                           14:'Spanish',
                           15:'other language'
                           }
    dic_prog_type = { 0 :'No programme type',
                      1 :'News',
                      2 :'Current Affairs',
                      3 :'Information',
                      4 :'Sport',
                      5 :'Education',
                      6 :'Drama',
                      7 :'Culture',
                      8 :'Science',
                      9 :'Varied',
                      10:'Pop Music',
                      11:'Rock Music',
                      12:'Easy Listening Music',
                      13:'Light Classical',
                      14:'Serious Classical',
                      15:'Other Music',
                      16:'Weather/meteorology',
                      17:'Finance/Business',
                      18:'Children\'sProgrammes',
                      19:'Social Affairs',
                      20:'Religion',
                      21:'Phone In',
                      22:'Travel',
                      23:'Leisure',
                      24:'Jazz Music',
                      25:'Country Music',
                      26:'National Music',
                      27:'Oldies Music',
                      28:'Folk Music',
                      29:'Documentary',
                      30:'Not used',
                      31:'Not used - skip indicator'                     
                     }
                     
    def init( self, bits ):
        self.base_flag          = bits[0]
        self.identity           = utility.bit_list_to_int(bits[1:3])
        self.rm_flag            = bits[3]
        
        # spectrum_occupancy
        if self.rm_flag == 0:
            #self.spectrum_occupancy = self.dic_so[utility.bit_list_to_int(bits[4:7])]
            self.spectrum_occupancy = utility.bit_list_to_int(bits[4:7])
        else:
            self.spectrum_occupancy = 100
            
        # interleaver_depth
        if self.rm_flag == 0:
            self.interleaver_depth = self.dic_interleaver_0[bits[7]]
        else:
            self.interleaver_depth = self.dic_interleaver_1[bits[7]]
        # msc mode
        self.msc_mode = utility.bit_list_to_int(bits[8:10])        
        
        # SDC mode
        if self.rm_flag == 0:
            self.sdc_mode_qam = self.dic_qam_0[bits[10]]
            self.sdc_mode_cr  = self.dic_cr_0[bits[10]]            
        else:
            self.sdc_mode_qam = self.dic_qam_1[bits[10]]
            self.sdc_mode_cr  = self.dic_cr_1[bits[10]]
        
        # Number of services
        self.audio_services = self.dic_audio_service[utility.bit_list_to_int(bits[11:15])]
        self.data_services  = self.dic_data_service[ utility.bit_list_to_int(bits[11:15])]
        
        # reconfiguration index
        self.reconfiguration_index = utility.bit_list_to_int(bits[15:18])
        
        # toggle flag
        self.toggle_flag = bits[18]
        
        # rfu
        self.rfu = bits[19]
        
        # SERVICE PARAMETERS
        self.service_identifier = bits[20:44]
        self.short_id           = bits[44:46]
        self.audio_ca           = bits[46]
        self.language           = self.dic_language[utility.bit_list_to_int(bits[47:51])]
        self.ad_flag            = bits[51]
        if self.ad_flag == 0:
            self.service_desc   = self.dic_prog_type[utility.bit_list_to_int(bits[52:57])]
        else:
            self.service_desc = bits[52:57]
        self.data_ca = bits[57]
        self.rfa     = bits[58:64]
            
    def print_fac(self):
        print( '\nFAC Informationen:')
        print( '\tSpectrum Occupancy : ' + str(self.spectrum_occupancy ) + 'khz' )
        print( '\tNumber of Audio Services : ' + str(self.audio_services) )
        print( '\tNumber of Data Services  : ' + str(self.data_services)  )
        print( '\tLanguage                 : ' + str(self.language)  )
        print( '\tSDC Modulation           : ' + str(self.sdc_mode_qam) + ' QAM')
        print( '\tMSC Information')
        print( '\t\tRM F                   : ' + str(self.rm_flag))
        print( '\t\tMode                   : ' + str(self.msc_mode))
        print( '\t\tInterleaver depth      : ' + str(self.interleaver_depth) )
        print( '' )