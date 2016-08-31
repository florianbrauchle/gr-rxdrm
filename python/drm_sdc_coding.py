# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 16:07:18 2016

@author: flo
"""
import numpy
import utility
# Rall 0.5 R0 0.5
# Puncturing Pattern:
# 1 
# 1 
# 0 
# 0 
# 0 
# fügt die beim Punktieren verlorenen Bits wieder ein (mit Wert null)
# und setzt die bitwerte zu -1(0) und 1 (1)
def dec_reform(bits_in, punctering_mode=0):
    punc_pat = [[1,1,0,0,0,0]] 
    
    m = 0
    n = 0
    len_out = len(bits_in) * 6 / 2 
    #print(len_out)

    # 3/5 mit aufgefülltem puncturing wird zu 1/4, also 3/12
    # 3/5 mit aufgefülltem puncturing wird zu 1/6, also 3/12 neuer Standard
    bits_out = [0] * len_out    
    #print( len( punc_pat[1]) )
    #print( len( punc_pat) )
    while m < len( bits_in ):
        for mask in punc_pat[(n/len(punc_pat[0]))%len(punc_pat)]:
            if mask == 0:  
                bits_out[n] = 0
            else:
                #print('in' + str(m) + ' out' + str(n) )
                bits_out[n] = int( ( bits_in[m] - 0.5 ) * 2 )
                m += 1
            n += 1
            
    return bits_out
    
    
    
    
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
        
data_entities={0:'Multiplex Description',
               1:'Label',
               2:'Conditional access parameters',
               3:'AFS: Multiple frequency Network information',
               4:'AFS: Schedule definition',
               5:'Application information',
               6:'Announcement support and switching',
               7:'AFS: Region definition',
               8:'Time and date information',
               9:'Audio information',
               10:'FAC channel parameters',
               11:'AFS: Other services',
               12:'Language and country',
               13:'AFS:detailed region definition',
               14:'Packet stream FEC parameters',
               15:'Extenstion'}
               
class sdc_info:
    dic_audio_coding = { 0:'AAC',
                         1:'reserved',
                         2:'reserved',
                         3:'xHE-AAC'}
    dic_sbr_flag     = { 0:'SBR not used',
                         1:'SBR used'}
    dic_audio_mode   = { 0:'mono',
                         1:'parametric stereo',
                         2:'stereo',
                         3:'reserved'}
    dic_audio_sr     = { 0:'reserved',
                         1:'12 kHz',
                         2:'reserved',
                         3:'24 kHz',
                         4:'reserved',
                         5:'48 kHz',
                         6:'reserved',
                         7:'reserved'}
               
    afs_index  = 0
    prot_lev_A = 0       
    prot_lev_B = 0       
    data_len_A = 0       
    data_len_B = 0
    
    short_id   = 0
    stream_id  = 0
        
    audio_code = ''
    sbr_flag   = ''
    audio_sr   = ''
    audio_mode = ''
    text_flag  = 0
    short_msg  = ''
    
    
    def init(self, bits):
        self.afs_index = ( utility.bit_list_to_int(bits[0:8]) ) 
            
        n = 8
        while n <= len(bits)-10:
            length  = utility.bit_list_to_int(bits[n:n+7])
            de_type = utility.bit_list_to_int(bits[n+8:n+12])
            data    = bits[n+12:n+12+4+length*8]
            
            if( de_type == 0 ):
                if ( length * 8 + 4 >= 28):
                    self.prot_lev_A = (utility.bit_list_to_int(data[0:2]))
                    self.prot_lev_B = (utility.bit_list_to_int(data[2:4]))
                    self.data_len_A = (utility.bit_list_to_int(data[4:16]) )
                    self.data_len_B = (utility.bit_list_to_int(data[16:28]) )
                        
            if( de_type == 1 ):
                string = ''
                for i in range(0, length):
                    string += chr( utility.bit_list_to_int(data[4+i*8:12+i*8]) )
                
                self.short_msg = string
                
            if( de_type == 9 ):
                    self.short_id  = utility.bit_list_to_int(data[0:2])
                    self.stream_id = (utility.bit_list_to_int(data[2:4]))
                    self.audio_code= self.dic_audio_coding[(utility.bit_list_to_int(data[4:6]))] 
                    self.sbr_flag  = self.dic_sbr_flag[data[6]] 
                    self.audio_mode= self.dic_audio_mode[utility.bit_list_to_int(data[7:9])] 
                    self.audio_sr  = self.dic_audio_sr[(utility.bit_list_to_int(data[9:12]) )]
                    self.text_flag = ((data[12]) )
#                        print ('   Enhance Flag: ' + str((data[13]) ))
#                        print ('   coder field : ' + str(utility.bit_list_to_int(data[14:19]) ))
#                        print ('   rfa         : ' + str((data[19]) ))
            n+=12 + 4 + length * 8
    
    
    def show_information(self):
        print( '\nSDC Information:')
        print( '\tAFS index: ' + str( self.afs_index ) )
        print( '\tShort Message : ' + self.short_msg )
        
        print ('\tDekodier Informatinen:')
        print ('\t\tProtection leel for part A: ' + str(self.prot_lev_A))
        print ('\t\tProtection leel for part B: ' + str(self.prot_lev_B))
        print('\t\tData Lenght for part A     : ' + str(self.data_len_A))
        print('\t\tData Lenght for part B     : ' + str(self.data_len_B))
        
        print ('\tAudio Informationen:')
        print ('\t\tShort Id    : ' + str(self.short_id) )
        print ('\t\tStream Id   : ' + str(self.stream_id) )
        print ('\t\tAudio coding: ' + self.audio_code)
        print ('\t\tSBR Flag    : ' + self.sbr_flag + '(nur für AAC, nicht xHE)')
        print ('\t\tAudio mode  : ' + self.audio_mode )
        print ('\t\tAudio sr    : ' + str(self.audio_sr) )
        print ('\t\tText Flag   : ' + str(self.text_flag) )
        
            
        