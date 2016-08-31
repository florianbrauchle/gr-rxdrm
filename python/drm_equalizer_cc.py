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

# Da dem Equalizer die Informationen aus dem FAC noch nicht zur Verfügung stehen,
# wird k_min und k_max maximal angenommen. 
# Dadurch entsteht etwas unnötiger overhead, der im Idealfall vermieden werden würde
# Allerdings ist die Funktion für alle Spectrum Occupancies gewährleistet.


import numpy
from gnuradio import gr

import pmt

import drm_parameter as drm
import utility as utility

class drm_equalizer_cc(gr.basic_block):
    """
    docstring for block drm_equalizer_cc
    """
    def __init__(self, p_info):
        gr.basic_block.__init__(self,
            name="drm_equalizer_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
            
        # Wichtige Parameter zur Entzerrung            
        self.mode    = 0
        self.so      = 0
        
        self.init_so = 0 # wird auf 1 gesetzt sobald so bekannt ist   
        self.new_so  = 0 
        
        # Parameter für EQ
        self.init_eq = 0
        self.kmin    = 0
        self.kmax    = 0
        
        self.spf     = 0
        
        self.ref_frame  = []
        self.rx_frame   = []
        self.diff_frame = []
        
        self.mode = 2
        self.set_output_multiple(1024 * drm.symbols_per_frame[self.mode] )
        
        self.block_len = 1024 * drm.symbols_per_frame[self.mode] 
        
        #Message Ports
        self.message_port_register_in(pmt.intern('fac_in'))
        self.set_msg_handler(pmt.intern('fac_in'), self.rx_fac)
        
        #Informationen ausgeben
        self.show_information = 1


    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        #self.consume_each(len(input_items[0]))
        
        output_items[0][0:self.block_len] = input_items[0][0:self.block_len]
        #Mode suchen und lernen
        tags = self.get_tags_in_range( 0, self.nitems_read(0), self.nitems_read(0) + len(input_items[0]) )
        for tag in tags:
            if pmt.symbol_to_string( tag.key ) == 'MODE':
                mode = pmt.symbol_to_string( tag.value)
                if mode == 'B':
                    self.mode = 2
                    self.spf  = drm.symbols_per_frame[self.mode]
                else:
                    # Nicht alle Modes implementiert
                    print('nur Mode B ist implementiert!')
                    self.mode = 0
        
        
        # Eigentlicher Equalizer
        # erste Initialisierung wenn Mode gefunden wurde
        if self.mode and self.init_eq == 0:
            self.eq_init()
            self.init_eq = 1
        
        if self.mode != 0:
            if self.new_so and self.show_information:
                #debug info
                self.eq_init()
                print('\nEQ')
                print( '\tSO ' + str(self.so) )
                print( '\tk_min : ' + str(self.kmin) + ' k_max : ' + str(self.kmax) )
            
            self.eq_frame(output_items[0][0:self.block_len])
            
            # Zusätzlich alle Referenzen auf 0 setzen, da hier sowieso die meisten Referenzen bekannt sind
            #gain
            for sym_in_frame in range(0, self.spf):
                # nicht genutzte Unterträger
                for k in drm.unused_subc[self.mode]:
                    output_items[0][(sym_in_frame*1024)+(512+k)] = 0
                
                # Gain Referenzen
                for k in range(self.kmin, self.kmax+1):
                    if( self.ref_frame[sym_in_frame][k-self.kmin] != 0 ):
                        output_items[0][(sym_in_frame*1024)+(512+k)] = 0
                        #input_items[0][(sym_in_frame*1024)+(512+k)] *= 10
                        
                # freq Referenzen
                for k in drm.freq_ref_sc:
                    output_items[0][(sym_in_frame*1024)+(512+k)] = 0
            #time 2 weil mode b, sollte angepasst werden auf alle modes. Aber keine zeit
            for k in drm.time_ref_sc[2]:
                output_items[0][(0*1024) + (512 + k)] = 0
            
        
        # Tag hinzufügen wenn sich so ändert bzw. gefunden wird
        if self.new_so == 1:
            key = pmt.string_to_symbol("SO")
            value = pmt.string_to_symbol(str(self.so))
            self.add_item_tag(0, self.nitems_written(0), key, value)
            self.new_so = 0
            
            
        # BIS ALLES LÄUFT HIER LASSEN, auch wenn alles läuft hier lassen
        self.consume(0, len(output_items[0][0:self.block_len]))
        return len(output_items[0][0:self.block_len])

    def rx_fac(self, msg):
        '''rx_fac empfängt die Nachricht des FAC\nDecoders und speichert die empfangenen Variablen ab
        
        '''
        rx_so  = int( pmt.symbol_to_string(pmt.cdr(msg)))
        if self.init_so == 0 or self.so != rx_so:
            self.so     = rx_so
            self.new_so = 1
        
        self.init_so = 1
        return 0
        
    def eq_init(self):
            self.kmin = drm.get_k_min(self.mode, self.so, self.init_so)
            self.kmax = drm.get_k_max(self.mode, self.so, self.init_so)
                
            self.ref_frame  = drm.get_gain_ref( self.mode, self.so, self.init_so)
            self.diff_frame = numpy.zeros(self.ref_frame.shape)
            
            self.init_eq    = 1
            
    def eq_frame(self, rx_symbols):
        self.diff_frame = numpy.zeros(self.ref_frame.shape, dtype=numpy.complex64)
    
        for sym_in_frame in range(0, self.spf):
            for k in range(self.kmin, self.kmax+1):
                if( self.ref_frame[sym_in_frame][k-self.kmin] != 0 ):
                    self.diff_frame[sym_in_frame][k-self.kmin] = self.ref_frame[sym_in_frame][k-self.kmin] / rx_symbols[(sym_in_frame*1024)+(512+k)]

        # interpoliere zwischen den Werten
        # interpolatioinsfunktion wurde gut getestet und funktioniert möglicherweise sogar
        utility.frame_interpolator(self.diff_frame, self.ref_frame)
       

        # Korrektur
        for sym_in_frame in range(0, self.spf):
            for k in range(self.kmin, self.kmax):
                rx_symbols[(sym_in_frame*1024)+(512+k)] = rx_symbols[(sym_in_frame*1024)+(512+k)]*self.diff_frame[sym_in_frame][k-self.kmin]
        
        #return self.diff_frame
        # tada
        