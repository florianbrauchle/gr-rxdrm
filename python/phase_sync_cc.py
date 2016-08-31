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



class phase_sync_cc(gr.sync_block):
    """
    docstring for block phase_sync_cc
    """
    def __init__(self, fs, fft_len, mode):
        gr.sync_block.__init__(self,
            name="phase_sync_cc",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        
        self.fs = 48000        
        self.mode = 0
        
        # OFDM Paramter aller 4 Modes festlegen
        # Im Moment nur für Mode B
        self.ofdm_freq_pilots = [16, 48, 64]
        self.ofdm_freq_phases = [331, 651, 555]
        self.ofdm_freq_abs    = numpy.sqrt(2)     
        # Phasen berechnen        
        self.ofdm_freq_phases = numpy.exp( numpy.multiply( (1j * 2 * numpy.pi / 1024), self.ofdm_freq_phases ) )
        # Amplitude berechnen
        self.ofdm_freq_ref    = numpy.multiply(self.ofdm_freq_phases, self.ofdm_freq_abs)
        self.ofdm_freq_phases = numpy.angle(self.ofdm_freq_phases)
        # Negative Frequenzen nach oben verschieben
        self.ofdm_freq_pilots =[x+512 for x in self.ofdm_freq_pilots]
        
        self.gi_len  = numpy.array([0,128,256,256,352])
        self.sym_len = numpy.array([0,1280,1280,960,800])
        self.fft_len = self.sym_len - self.gi_len
        self.modes  = ['Nicht erkannt', 'A', 'B', 'C', 'D']
        
        #bzw. self.fft_len
        # wird erst relevant, sobald Mode erkannt...
        self.set_output_multiple(1024)
        
        self.phase_offset = 0
        
        self.ncnt = 0
    
        # Logger
        self.log = gr.logger( 'log_debug' )   
        self.log.debug('DEBUG LOG')
        self.log.set_level('DEBUG')

    def work(self, input_items, output_items):
        # Phasenfehler berechnen
        a_symbol = 0
        p_symbol = [0,0,0]
        for a in range(0,len(self.ofdm_freq_pilots) ):
            a_symbol   += numpy.abs(input_items[0][ self.ofdm_freq_pilots[a] ]) #/ self.ofdm_freq_abs
            p_symbol[a] = numpy.angle(input_items[0][ self.ofdm_freq_pilots[a] ]) - self.ofdm_freq_phases[a]
            #p_symbol[a] += 2*numpy.pi
#            print( '\tIst: ' + str(numpy.angle(input_items[0][ self.ofdm_freq_pilots[a] ])) 
#                  +' Soll: ' + str(numpy.angle(self.ofdm_freq_ref[a])) 
#                  +' Fehler: ' + str(p_symbol[a]))


        
        a_symbol = a_symbol / len(self.ofdm_freq_pilots)  
        #p_symbol = p_symbol / len(self.ofdm_freq_pilots)
        
        # Phasensprünge erkennen, vorraussetzung ist dPhi < pi
        d_ph = p_symbol[2]-p_symbol[1]
        if numpy.abs( d_ph ) >= numpy.pi:
            p_symbol[2] -= numpy.sign( d_ph ) * numpy.pi * 2
        d_ph = (p_symbol[2]-p_symbol[1])/(self.ofdm_freq_pilots[2]-self.ofdm_freq_pilots[1])
        
        #phasen berechnen
        korr_phases = numpy.zeros(1024)         
            
        for a in range(0,self.ofdm_freq_pilots[1]):
            korr_phases[a] = p_symbol[1] - (self.ofdm_freq_pilots[1]-a)   * d_ph
        for a in range(self.ofdm_freq_pilots[1],len(korr_phases)):
            korr_phases[a] = p_symbol[1] + (a - self.ofdm_freq_pilots[1]) * d_ph
        
        korr_phases = numpy.multiply( 1/a_symbol, numpy.exp( -1j * korr_phases ) )
        
        a_symbol = self.ofdm_freq_abs / a_symbol

        output_items[0][0:1024] = numpy.multiply(input_items[0][0:1024], korr_phases )
        return 1024

