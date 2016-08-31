# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 16:07:18 2016

@author: flo
"""
import numpy
import utility





# sollte stimmen
def cell_interleaver(bits_in, long_int = 1):
    #p   = [0,1,2] # for FAC p = 0
    xi  = len(bits_in[0])
    D   = len(bits_in)
    
    s   = numpy.power( 2, numpy.ceil( numpy.log2(xi) ) )
    q   = s/4 - 1
    t_0  = 5
    
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
        cap_tau  = int( i % D )
        bits_out[cap_pi_0] = bits_in[cap_tau][i]
        

    return bits_out
    



def qam_16_demod( sym_in ):
    a = 1 / numpy.sqrt(10)
    
    bits_out_0 = [0] * int( 2 * len(sym_in) )
    bits_out_1 = [0] * int( 2 * len(sym_in) )
    for sym in range(0, len(sym_in)):
        i_0 = 0
        i_1 = 0
        q_0 = 0
        q_1 = 0
        
        if numpy.imag( sym_in[sym] ) < 0:
            q_1 = 1
            
        if 0 < numpy.imag( sym_in[sym] ) < 2*a:
            q_0 = 1
        if numpy.imag( sym_in[sym] ) < -2*a:
            q_0 = 1
        
        
        if numpy.real( sym_in[sym] ) < 0:
            i_1 = 1
            
        if 0 < numpy.real( sym_in[sym] ) < 2*a:
            i_0 = 1
        if numpy.real( sym_in[sym] ) < -2*a:
            i_0 = 1
                 
        #print('real: ' + str(numpy.real(sym_in[sym])*numpy.sqrt(10)) + ' imag: ' + str(numpy.imag(sym_in[sym])*numpy.sqrt(10)) )
        bits_out_0[2*sym:2*sym+2] = [i_0, q_0]
        bits_out_1[2*sym:2*sym+2] = [i_1, q_1]
        

    return [bits_out_0, bits_out_1]

def departioning_of_information(bits_0, bits_1):
    ''' nimmt bit stream 0 und 1 und fügt sie zusammen '''
    # zuerst die besser geschützten bits
    bits = list(bits_0) + list(bits_1)
    # und selbst hier schleichen sich fehler ein...
    # ok, diese funktion ist jetzt vll. doch etwas überflüssig
    
    return bits

# Rall 0.5 R0 0.5
# Puncturing Pattern:
# 1 
# 1 
# 0 
# 0 
# 0 
# fügt die beim Punktieren verlorenen Bits wieder ein (mit Wert null)
# und setzt die bitwerte zu -1(0) und 1 (1)
def dec_reform(bits_in, protection_level = 0, stream = 0):
    #protection level 0  Rall 0.5; R0 = 1/3; R1 = 2/3; RYicm = 3
    #protection level 1 Rall 0.62; R0 = 1/2; R1 = 3/4; RYicm = 4
    punc_patterns = [ [[1,1,1,0,0,0]], # 1/3 
                      [[1,1,0,0,0,0],[1,0,0,0,0,0]] , # 2/3 
                      [[1,1,0,0,0,0]] , # 1/2 
                      [[1,1,0,0,0,0],[1,0,0,0,0,0],[1,0,0,0,0,0]] ] # 3/4 
    
    tail_pat_n    = [ 0, 0 , 0, 2]                      
    punc_pat_tail = [  [[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0]],
                       [[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0]], 
                       [[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0],[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0]], 
                       [[1,1,1,0,0,0],[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,0,0,0,0]], 
                       [[1,1,1,0,0,0],[1,1,1,0,0,0],[1,1,0,0,0,0],[1,1,1,0,0,0],[1,1,1,0,0,0],[1,1,0,0,0,0]] ]
                       
    punc_pat_tail_n_bits = [12,13,14,15,16,17,18]
    rates = [2, 4, 3, 4.5 ]
    
    tail_bits = bits_in[-punc_pat_tail_n_bits[tail_pat_n[2*protection_level+stream]]: ]
    bits      = bits_in[0:-punc_pat_tail_n_bits[tail_pat_n[2*protection_level+stream]]]
    punc_pat = punc_patterns[2*protection_level+stream]
    
    
    m = 0
    n = 0
    len_out = len(bits) * rates[2*protection_level+stream]
    len_out = int( numpy.ceil(len_out))
    #print(len_out)


    bits_out = [0] * (len_out)  
    
    while m < len( bits ):
        #print( (n/len(punc_pat[0]))%len(punc_pat) )
        for mask in punc_pat[(n/len(punc_pat[0]))%len(punc_pat)]:
            if mask == 0:  
                bits_out[n] = 0
            else:
                #print('in' + str(m) + ' out' + str(n) )
                bits_out[n] = int( ( bits[m] - 0.5 ) * 2 )
                m += 1
            n += 1
    #print('in' + str(m) + ' out' + str(n) )
            
    
    m = 0
    n = 0        
    tail_bits_out = [0]*36
    punc_pat = punc_pat_tail[tail_pat_n[2*protection_level+stream]]
    while m < len( tail_bits ):
        #print( (n/len(punc_pat[0]))%len(punc_pat) )
        for mask in punc_pat[(n/len(punc_pat[0]))%len(punc_pat)]:
            if mask == 0:  
                tail_bits_out[n] = 0
            else:
                #print('in' + str(m) + ' out' + str(n) )
                tail_bits_out[n] = int( ( tail_bits[m] - 0.5 ) * 2 )
                m += 1
            n += 1

    return bits_out + tail_bits_out
    
    
    
    
def crc_check(bits_in):
    #x16 + x12 + x5 + 1
    shift_reg = numpy.ones(16)
    shift_reg_old = shift_reg
    for i in range( 0, len(bits_in) ):
        shift_reg_old = list(shift_reg)
        bit_add = (bits_in[i] + shift_reg_old[0])%2
        shift_reg[15]  = bit_add
        shift_reg[14]  = shift_reg_old[15]
        shift_reg[13]  = shift_reg_old[14]
        shift_reg[12]  = shift_reg_old[13]
        shift_reg[11]  = shift_reg_old[12]
        shift_reg[10]  = (shift_reg_old[11] + bit_add)%2
        shift_reg[9]   = shift_reg_old[10]
        shift_reg[8]   = shift_reg_old[9]
        shift_reg[7]   = shift_reg_old[8]
        shift_reg[6]   = shift_reg_old[7]
        shift_reg[5]   = shift_reg_old[6]
        shift_reg[4]   = shift_reg_old[5]
        shift_reg[3]   = (shift_reg_old[4] + bit_add)%2
        shift_reg[2]   = shift_reg_old[3]
        shift_reg[1]   = shift_reg_old[2]
        shift_reg[0]   = shift_reg_old[1]
    
    if numpy.sum(shift_reg) == 0:
        return 1
    else:
        return 0

class text_message:
    segment = []
    message = []
    
    start_detected  = 0 
    
    def clear_message(self):
        self.message = []
    def clear_segment(self):
        self.segment = []
    
    def crc_check(bits_in):
        #G 16 (x) = x 16 + x 12 + x 5 + 1.
        shift_reg = numpy.ones(16)
        shift_reg_old = shift_reg
        for i in range( 0, len(bits_in) ):
            shift_reg_old = list(shift_reg)
            bit_add = (bits_in[i] + shift_reg_old[0])%2
            shift_reg[15]  = bit_add
            shift_reg[14]  = shift_reg_old[15]
            shift_reg[13]  = shift_reg_old[14]
            shift_reg[12]  = shift_reg_old[13]
            shift_reg[11]  = shift_reg_old[12]
            shift_reg[10]  = (shift_reg_old[11] + bit_add)%2
            shift_reg[9]   = shift_reg_old[10]
            shift_reg[8]   = shift_reg_old[9]
            shift_reg[7]   = shift_reg_old[8]
            shift_reg[6]   = shift_reg_old[7]
            shift_reg[5]   = shift_reg_old[6]
            shift_reg[4]   = shift_reg_old[5]
            shift_reg[3]   = (shift_reg_old[4] + bit_add)%2
            shift_reg[2]   = shift_reg_old[3]
            shift_reg[1]   = shift_reg_old[2]
            shift_reg[0]   = shift_reg_old[1]
        
        if numpy.sum(shift_reg) == 0:
            return 1
        else:
            return 0
        
    def add_bits(self, bits_in):
        #print('Bits in Textmessage: ' + str(bits_in) )
        if numpy.sum(bits_in) == len(bits_in):
            if len(self.segment) >= 32 and self.start_detected:
                # Beginn eines Segments
                header = self.segment[0:16]
                body   = self.segment[16:-16]
                crc    = self.segment[-16:]            
                
                h_toggle = header[0]
                h_first  = header[1]
                h_last   = header[2]
                h_command= header[3]
                h_field1 = header[4:8]
                h_field2 = header[8:12]
                h_rfa    = header[12:16]
                
                # Variablen
                body_len = 0
                command  = 0
                seg_num  = 0
                
                if h_command:
                    body = []
                    command = utility.bit_list_to_int(h_field1)
                else:
                    body_len = utility.bit_list_to_int(h_field1)
                    body_len += 1
                    if len(body)/8 > body_len:
                        body = body[0:8*body_len]
                    seg_num  = utility.bit_list_to_int(h_field2[1:])
                
                if h_first:
                    #print('1. Segment der Textnachricht empfangen!')
                    self.clear_message()
                    self.message += body
                    
                if h_last:
                    print('Letztes Segment der Textnachricht empfangen!')

                    
                    max_str = len(self.message)/8
                    
                    string = ''
                    for i in range(0, max_str):
                        #print(' i :  ' + str(i) )
                        #print( str(self.message[i*8:8+i*8]) )
                        #print(chr( utility.bit_list_to_int(self.message[i*8:8+i*8]) ))
                        char = chr( utility.bit_list_to_int(self.message[i*8:8+i*8]) )
                        if char != chr(0):
                            string += char
                            #print( string )
                    print( 'Textmessage:  ' + string )
                    self.clear_message()
                
                if not h_first and not h_last:
                    #print('Segment der Textnachricht empfangen!')
                    self.message += body
            else:
                self.start_detected = 1
                
            self.clear_segment()
        else:
            #self.segment.append(bits_in)
            self.segment = self.segment + bits_in
            #print('Segment länge: ' + str(len(self.segment)) )
        
        #print('Länge der Nachricht: ' + str(len(self.message)) )
            
    
            
            
