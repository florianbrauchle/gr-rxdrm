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

    
class framer_cc(gr.basic_block):
    """
    docstring for block framer_cc
    """
    def __init__(self, mode, p_corr_limit, print_values):
        gr.basic_block.__init__(self,
            name="framer_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        # Parameter
        self.corr_limit = p_corr_limit      
        self.print_values = print_values
            
            
        self.set_output_multiple(1024)
        # referenz werte
        self.frame_ref_n = numpy.array([ 14,  16,  18,  20,  24,  26, 32,  36,  42,  44,  48,  49,  50,  54,  56,  62,  64,  66,  68])
                
        self.frame_ref_ph = numpy.array([304, 331, 108, 620, 192, 704, 44, 432, 588, 844, 651, 651, 651, 460, 460, 944, 555, 940, 428])
        #self.ref_pairs    = [[49,50],[54,55]]
        self.frame_ref_ph = self.frame_ref_ph / 1024.0
        self.frame_ref_am = numpy.sqrt(2) 
        
        self.frame_ref = self.frame_ref_am * numpy.exp( 1j * 2 * numpy.pi * self.frame_ref_ph)
        
        # Kontrollstruktur
        self.symbl_cnt = 0
        self.frame_cnt = 0
        self.new_frame_detected = 0
        
        self.initial_frame_detected = 0
        self.items_created = 0
        
    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
#        output_items[0][:] = input_items[0]
#        self.consume(0, len(input_items[0]))
        
        # Warte auf Frame Anfang
        # Sende Daten weiter
            
        # Berechnung der Korrelation
        # Um Mode unabhängig zu funktionieren müssen die referenzen als mehrdimensionale arrays gespeichert werden
        # und der Mode über den Tag bestimmt werden
        corr_val = 0
        norm_a = 0
        norm_b = 0
        norm = 0
        max_corr = 0
        
        corr_val = 0
        norm_a = 0
        norm_b = 0
        norm = 0
        for s in range(0, len(self.frame_ref_n) ):
            corr_val += numpy.multiply(input_items[0][512+self.frame_ref_n[s]],numpy.conj(self.frame_ref[s]))
            norm_a   += numpy.conj(self.frame_ref[s]) * self.frame_ref[s]
            norm_b   += numpy.conj(input_items[0][512+self.frame_ref_n[s]]) * input_items[0][512+self.frame_ref_n[s]]
        norm = numpy.sqrt(norm_a * norm_b)
        max_corr = corr_val/norm
        
        # Alternativ, ber. Anhand der Signalenergie
#        avg_amp = 0
#        for s in self.frame_ref_n:
#            avg_amp += numpy.square(numpy.abs(input_items[0][512+s]))
        #print( 'Power: ' + str( avg_amp / len(self.frame_ref_n) ))
         
         
        # Funktion um die Korrelationswerte anzuzeigen, hilft zum justieren des Gernzwertes
        if self.print_values:
            print('Frame Korrelationsmaximum : ' + str(numpy.abs(max_corr) ) )
                
                
        # Zählt die Symbole seit dem letzten Frame beginn
        self.symbl_cnt += 1

                
        # Wenn die Korrelation den gesetzten Grenzwert übersteit wird ein neuer Frame detektiert
        if max_corr > self.corr_limit:
            self.frame_cnt += 1
            self.symbl_cnt = 0
            # Tag hinzufügen
            key = pmt.string_to_symbol("FRAME")
            value = pmt.string_to_symbol(str(self.frame_cnt))
            self.add_item_tag(0, self.nitems_written(0), key, value)
            self.initial_frame_detected = 1
        
        
        # Sobald ein Frame detektiert wurde, werden die OFDM-Symbole durchgereicht
        if self.initial_frame_detected != 0 and self.symbl_cnt <= 16:
            output_items[0][0:1024] = input_items[0][0:1024]
            self.items_created = 1024
            
        self.consume(0, 1024 )
        return self.items_created
