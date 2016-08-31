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

#DRM Parameter
import drm_parameter as drm



class fsync_cc(gr.basic_block):
    """
    docstring for block fsync_cc
    """
    def __init__(self, p_integ):
        gr.basic_block.__init__(self,
            name="fsync_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        # Parameter
        self.set_output_multiple(2048)
        self.freq_range = 10
        self.ofdm_pilots = [16, 48, 64]
        
        # Mode A
        
        # Mode B
        
        
        # Iniitialisierungen
        self.mode    = 0
        
        self.ffactor = 0
        self.items_consumed = 0
        self.items_created = 0
        
        self.offset = 0
        self.var    = 100
        
        # Logger
        self.log = gr.logger( 'log_debug' )   
        self.log.debug('DEBUG LOG')
        self.log.set_level('ERROR')
        
        
        
        # Schätzer aktivieren
        self.enable_integration = p_integ
        #Schätzer über mehrere Symbolef
        self.estimation_k    = 0.0
        self.n_estimations   = 0.0
        self.estim_var_start = 100.0 # var des Schätzers, recht groß in manchen fällen für grobe f sync
        self.confidence      = self.estim_var_start


    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items
            
            
            
    def shift_symbol(self, symbol_1, freq_off_est):
        if freq_off_est < 0:
            temp_symbol = list(symbol_1)
            symbol_1[0:-1*freq_off_est] = temp_symbol[len(temp_symbol)+freq_off_est:]
            symbol_1[-1*freq_off_est:]  = temp_symbol[0:len(temp_symbol)+freq_off_est]
        elif freq_off_est > 0:
            temp_symbol = list(symbol_1)
            symbol_1[0:len(symbol_1)-freq_off_est] = temp_symbol[freq_off_est:]
            symbol_1[len(symbol_1)-freq_off_est:]  = temp_symbol[0:freq_off_est]
        return symbol_1



    def general_work(self, input_items, output_items):
        
        self.log.debug('\nFreq Sync' )
        self.items_consumed = len(input_items[0])
        self.items_created = 0
        
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
            # Symbole ausschneiden
            symbol_1 =  numpy.fft.fftshift(numpy.fft.fft(input_items[0][0:1024]))
            symbol_2 =  numpy.fft.fftshift(numpy.fft.fft(input_items[0][1024:2048]))
            
            
            # Berechnung des Groben Frequenzfehlers
            freq_off = numpy.zeros([self.freq_range*2+1], 'complex')
            for k in range(-self.freq_range,self.freq_range+1):
                norm_a = 0
                norm_b = 0
                for s in self.ofdm_pilots:
                    freq_off[k+self.freq_range] += numpy.multiply(symbol_1[512+s+k],numpy.conj(symbol_2[512+s+k]))
                    norm_a                      += numpy.multiply(symbol_1[512+s+k],numpy.conj(symbol_1[512+s+k]))
                    norm_b                      += numpy.multiply(symbol_2[512+s+k],numpy.conj(symbol_2[512+s+k]))
                freq_off[k+self.freq_range] = freq_off[k+self.freq_range]/numpy.sqrt(norm_a * norm_b)
                    
            
            freq_off     = numpy.abs(freq_off)
            freq_off_est = numpy.argmax(freq_off) - self.freq_range
            
            
            if self.enable_integration:
                # Schätzer über Zeit integrireren
                # Nur möglich, wenn delta F konstant
                self.n_estimations += 1.0
                N = self.n_estimations
                self.estimation_k = self.estimation_k * ( N - 1 ) / N + (freq_off_est/N)
                # Die Varianz des Schätzers wird als bekannt vorausgesetzt, bzw. sollte lieber über als unterschätzt werden
                self.confidence = self.estim_var_start / N
                freq_off_est = int(numpy.round( self.estimation_k ))
            
            # Frequenzfehler korregieren
            # Im Frequenzbereich eine einfache Verschiebung
            symbol_1 = self.shift_symbol(symbol_1, freq_off_est)
            symbol_2 = self.shift_symbol(symbol_2, freq_off_est)
            
            
            self.ffactor = 1
            output_items[0][0        :  1024] = symbol_1
            output_items[0][1024     :  2048] = symbol_2
            
            self.items_consumed = 2048
            self.items_created  = 2048
            
            self.log.debug('\tFreq Offset: '        + str( freq_off_est  * 46.875))   
            self.log.info( '\tGrober Freq Offset: ' + str( freq_off_est  * 46.875))                  
            self.log.debug('\tFreq Sync erfolgreich\n')      
            
        
        
        self.consume(0, self.items_consumed )
        return self.items_created


