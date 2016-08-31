#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2016 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

import pmt

import drm_fac_coding as fac_dec
import drm_parameter as drm


class fac_decode_c(gr.sync_block):
    """
    docstring for block fac_decode_c
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="fac_decode_c",
            in_sig=[numpy.complex64],
            out_sig=None)
            
        # Variablen
        self.fac_recvd = 0
        self.fac_block = [0] * 65
        
        # Message Ports
        self.message_port_register_out(pmt.intern('fac_out'))
        
        # FAC Informationen
        self.spectrum_occupancy = 0
        self.fac_decoder = fac_dec.fac_data()
        
        self.spectrum_occupancy = 0
        self.send_so = 0


    def work(self, input_items, output_items):

        
        # warte auf ganzen FAC Block
        len_recvd = self.fac_recvd + len(input_items[0])
        n_fac     = int(numpy.floor( len_recvd / 65 ))
        
        #print('FAC Symbols: ' + str(len(input_items[0])) + ' n=' + str(n_fac) )
        for n in range(0, n_fac):
                missing_bits = 65-self.fac_recvd
                self.fac_block[self.fac_recvd:65] = input_items[0][0:missing_bits]
                #print( self.fac_block )
                
                #Demodulation
                bits = fac_dec.qam_slicer(self.fac_block)
                #print( bits )
                #print( 'LEN: ' + str(len(bits)) )
                
                # Bit Deinterleaving
                bits = fac_dec.bit_deinterleaving(bits)  
                #print( 'DINTER LEN: ' + str(len(bits)) )              
                
                #Viterbi
                bits    = fac_dec.dec_reform(bits)
                decoder = fac_dec.viterbi()
                bits    = decoder.decode(bits)
                #print( 'LEN: ' + str(len(bits)) )
                
                #Energy Dispersal
                bits    = fac_dec.scrambler(bits[0:72])
                #print( 'LEN: ' + str(len(bits)) )
                
                # crc bits invertieren
                #crc = bits[64:72]
                crc = [ int((x+1)%2) for x in bits[64:]]
                bits = [ int(x) for x in bits[0:64]]
               
                if fac_dec.crc_check(bits[0:64]+crc):
                    self.fac_decoder.init(bits[0:64])
                    #self.fac_decoder.print_fac()
                    if self.spectrum_occupancy != self.fac_decoder.spectrum_occupancy:
                        self.spectrum_occupancy = self.fac_decoder.spectrum_occupancy
                        msg = pmt.cons(pmt.string_to_symbol('SO'), pmt.string_to_symbol(str(self.spectrum_occupancy) ) )
                        self.message_port_pub(pmt.intern('fac_out'), msg)                      
                        
                else:
                    print( ' FAC CRC Fehler! ')
                #FERTIG
                

                
                
                self.fac_recvd = 0
                len_recvd -= 65
                
                #print('FAC Decoded!')
        
        if len_recvd > 0:
            self.fac_block[0:len_recvd] = input_items[0][n_fac * 65:]
        
        return len(input_items[0])

