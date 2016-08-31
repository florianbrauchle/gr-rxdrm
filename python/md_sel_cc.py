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
import numpy as np
from gnuradio import gr
import pmt


    
    
class md_sel_cc(gr.basic_block):
    """
    Mode selection for the DRM receiver
    """    
        
    def __init__(self, p_integ):
        gr.basic_block.__init__(self,
            name="md_sel_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        # Parameter
        self.offset = 210 # in simulation bestimmt
        
        self.fs = 48000        
        #
        self.generated_samples = 0
        self.symbol_found = 0
        self.symbol_start = 0
        self.symbol_start_offset = 0
        # Symbollänge + buffer, um zu verhindern das Maxima direkt nach dem Symbol vorkommen
        #self.set_history(1024+256+30)
            #set multiple
        #self.set_
        #self.set_history((1024+256)*2)
        self.set_output_multiple(1024*2)
        self.mode = 0
        
        # OFDM Paramter aller 4 Modes festlegen
        self.gi_len  = np.array([0, 128, 256,256,352])
        self.sym_len = np.array([0,1280,1280,960,800])
        
        self.modes  = ['Nicht erkannt', 'A', 'B', 'C', 'D']
        
        # Time Sync
        self.est_t   = 0
        self.found_t = 0
        
        # Mode Detection
        self.new_mode_detected = 0
        
        # Fine Freq Sync
        self.fine_freq_off = 0
    
        # Logger
        self.log = gr.logger( 'log_debug' )   
        self.log.debug('DEBUG LOG')
        self.log.set_level('ERROR')
        
        
        # Schätzer aktivieren
        self.enable_integration = p_integ
        # Schätzer über Zeit integrieren Zeitsync
        self.n_estimations_t    = 0.0
        self.estimation_t       = 0.0
        self.confidence_t       = 0.0
        self.estim_var_t        = 100.0 # Varianz des Schätzers, rech klein bei der feinen Freq sync
        # Schätzer über Zeit integrieren Zeitsync
        self.n_estimations_f    = 0.0
        self.estimation_f       = 0.0
        self.confidence_f       = 0.0
        self.estim_var_f        = 10.0 # Varianz des Schätzers, rech klein bei der feinen Freq sync
        
        
        #print( gr.logger_get_names() )
        

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            #print(str(noutput_items * (1280.0 / 1024.0)))
            ninput_items_required[i] = int(numpy.ceil(noutput_items * (1280.0 / 1024.0)))



    def gi_correlation(self, p_gi_len, p_symbol_len, signal):
        ''' Mode Erkennung '''
        corr_delay = p_symbol_len - p_gi_len 
        
        # Verzögertes Signal / Delay
        corr_A = signal[0:p_gi_len-1];
        corr_B = signal[corr_delay:len(signal)-1] 
        
        # Normierung
        corr_A =  corr_A / np.sqrt( np.sum(np.square(np.abs(corr_A))) )
        corr_B =  corr_B / np.sqrt( np.sum(np.square(np.abs(corr_B))) )
        
        # Korrelation
        erg_corr = np.correlate(corr_A,corr_B)
            
        return erg_corr[0]
        
    def mode_selection(self, signal):
        corr_res_A = np.zeros( 1280 )
        corr_res_B = np.zeros( 1280 )
        corr_res_C = np.zeros( 1280 )
        corr_res_D = np.zeros( 1280 )
        for s in range(0, 1280):
            corr_res_A[s] = np.abs(self.gi_correlation(128, 1280, signal[s: s+1280-1] ))
            corr_res_B[s] = np.abs(self.gi_correlation(256, 1280, signal[s: s+1280-1] ))
            corr_res_C[s] = np.abs(self.gi_correlation(256, 960, signal[s: s+960-1] ))
            corr_res_D[s] = np.abs(self.gi_correlation(352, 800, signal[s: s+800-1] ))
        corr_max = np.zeros(4)
        corr_max[0] = np.max( corr_res_A )
        corr_max[1] = np.max( corr_res_B )
        corr_max[2] = np.max( corr_res_C )
        corr_max[3] = np.max( corr_res_D )
        
        mode = np.argmax( corr_max ) + 1        
        
        # Detektierten Mode speichern
        self.mode = mode
        
        # Ausgangssamples auf die richtige Länge setzen
        self.set_output_multiple( self.sym_len[self.mode] )
        
        # Starten der Zeitsynchronisation
        self.new_mode_detected = 1
                
        
        
        return
        
        
        
    """
    Zeit Synchronisation
    """         
    def time_sync(self, signal, start_est, stop_est):
        self.symbol_found = 0
        self.symbol_start = 0
        self.log.debug('time_sync()')      
        corr_res = np.zeros( self.sym_len[self.mode], dtype=complex)
        for s in range(start_est, self.sym_len[self.mode]-1):
            corr_res[s] = self.gi_correlation(self.gi_len[self.mode], self.sym_len[self.mode], signal[s: s+self.sym_len[self.mode]] )
        corr_max = np.argmax( np.abs(corr_res) )     
        
        self.symbol_found = 1
        self.symbol_start = corr_max + 256 - 20
        self.generated_samples = self.sym_len[self.mode] - self.gi_len[self.mode]
            
        # Tracking
        self.fine_freq_off = np.angle(corr_res[corr_max])/(2*np.pi*(self.sym_len[self.mode] - self.gi_len[self.mode])*(1.0/self.fs))
            
        return   
        
    def mixer( self, p_signal, p_freq, p_fs ):
        time = np.linspace(0, len(p_signal)-1,len(p_signal))
        time = time * (1.0/p_fs)
        m_func =  p_signal * np.exp(-1j*2*np.pi*p_freq*time)
        return m_func


    def general_work(self, input_items, output_items):
        self.generated_samples = 0
        # Mode Selection
        if(self.mode == 0):
            self.mode_selection(input_items[0][0:1280+1280])
        else:
            # Zeit Synchronisation
            self.time_sync( input_items[0][0:self.sym_len[self.mode]*2-1], 0, 1280 )
            # Feine Frequenzsynchronisation 
        
        if self.symbol_found == 1:
            if self.enable_integration:
                # Schätzer über Zeit integrireren
                # Nur möglich, wenn delta F konstant
                self.n_estimations_f += 1
                N = self.n_estimations_f
                self.estimation_f = self.estimation_f * ( N - 1 ) / N + (self.fine_freq_off/N)
                # Die Varianz des Schätzers wird als bekannt vorausgesetzt, bzw. sollte lieber über als unterschätzt werden
                self.confidence_f = self.estim_var_f / N
                
                # Schätzer über Zeit integrireren
                # Nur möglich, wenn delta F konstant
                self.n_estimations_t += 1
                N = self.n_estimations_t
                self.estimation_t = self.estimation_t * ( N - 1 ) / N + (self.symbol_start/N)
                # Die Varianz des Schätzers wird als bekannt vorausgesetzt, bzw. sollte lieber über als unterschätzt werden
                self.confidence_t = self.estim_var_t / N
                
                self.fine_freq_off = self.estimation_f
                self.symbol_start  = int(numpy.round(self.estimation_t))
                
            
            # Frequenzkorrektur                        
            output_items[0][0:self.generated_samples] = self.mixer(input_items[0][self.symbol_start:self.symbol_start + self.generated_samples ], -1*self.fine_freq_off, self.fs)   
            
            
            # Wird der Symbolanfang direkt auf null gesetzt, wird bei der korrelation teilweise erst das 2. symbol erkannt
            self.symbol_start_offset = 256 - self.symbol_start
            self.estimation_t += self.symbol_start_offset
                
            # Tag hinzufügen
            if self.new_mode_detected == 1:
                key = pmt.string_to_symbol("MODE")
                value = pmt.string_to_symbol(self.modes[self.mode])
                self.add_item_tag(0, self.nitems_written(0), key, value)
                self.new_mode_detected = 0
            

            
        self.consume(0,self.sym_len[self.mode] - self.symbol_start_offset)
        self.symbol_start_offset = 0
        
        return self.generated_samples
