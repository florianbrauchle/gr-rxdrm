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

class mixer_cc(gr.basic_block):
    """
    Der Mixer bringt das Signal auf den Richtigen Unterträgerabstand für die FFT
    Also:
        xxx Hz Mode A
        xxx Hz Mode B
        xxx Hz Mode C
        xxx Hz Mode D
    """
            
    
    def __init__(self, mode, fs):
        gr.basic_block.__init__(self,
            name="mixer_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.mode = mode
        self.ffactor = 1
        self.set_output_multiple(1028)
        
        # Sonstiges
        self.samples_generated = 0
        
        # Logger
        self.log = gr.logger( 'log_debug' )   
        self.log.debug('DEBUG LOG')
        self.log.set_level('DEBUG')

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = self.ffactor * noutput_items

    def general_work(self, input_items, output_items):
        # Als erstes muss der Mode erkannt werden, dazu wird einfach nach dem Mode Tag gesucht
        self.log.debug('\nMixer (namen ändern!)' )
        
        tags = self.get_tags_in_range( 0, self.nitems_read(0), self.nitems_read(0) + len(input_items[0]) )
        for tag in tags:
            if pmt.symbol_to_string( tag.key ) == 'MODE':
                mode = pmt.symbol_to_string( tag.value)
                if mode == 'B':
                    self.mode = 2
                else:
                    self.log.debug('\tMode ' + mode + ' nicht implementiert' )
                    
                self.log.debug('\tMode ' + mode + ' eingestellt' )
                    
        if self.mode == 2:
            #Frequenzanpassen...
            #Zeugs tun
            #forecast anpassen
            # Für A und B stimmt 1
            
            self.ffactor = 1
            
            
            self.samples_generated = 1024
            
            self.log.debug('\tUnterträgerabstand eingestellt')      
            
        
        self.samples_generated = 1024
        output_items[0][0:1024] = input_items[0][0:1024]
        self.consume(0, 1024)
        #self.consume_each(len(input_items[0]))
        return self.samples_generated
