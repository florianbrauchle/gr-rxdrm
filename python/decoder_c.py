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

import drm_parameter as drm
import drm_fac_coding as fac_dec
import drm_sdc_coding as sdc_dec
import drm_msc_coding as msc_dec


class decoder_c(gr.sync_block):
    """
    docstring for block decoder_c
    """
    def __init__(self, p_info):
        gr.sync_block.__init__(self,
            name="decoder_c",
            in_sig=[numpy.complex64],
            out_sig=None)
        
        # Message Ports
        self.message_port_register_out(pmt.intern('fac_out'))
            
        # Variablen
        self.mode = 0   
        self.eq_so_true = 0
        
        # SO and Frame information
        self.spf  = 0        
        self.kmin = 0
        self.kmax = 0
        
        # FAC Informationen
        self.fac_sym = []
        self.fac_decoder = fac_dec.fac_data()
        self.spectrum_occupancy = 0
        self.send_so = 0
        
        # SDC Information
        self.sdc_mod = 0
        self.fdc_sym = []
        self.sdc_dec = sdc_dec.sdc_info()
        
        # MSC Information
        self.new_superframe = 0
        self.superframe     = [0] * (drm.msc_qam_cells[2][3] )#- drm.msc_qam_cells_loss[2][3])
        self.start_msc      = 0
        self.enough_mux_frames = 0
        self.n_rcvd_mux_frames = 0
        self.msc_mux_frames = [ [],[],[],[],[],[],[],[],[] ]
        self.msc_decell     = [[],[],[]]
        self.msc_sym = []
        self.msc_symbols_recvd = 0
        self.start_msc_decode =0
        
        self.show_fac_information = p_info
        self.show_sdc_information = p_info
        
        # Textmessage in MSC
        self.text_massage = msc_dec.text_message()

    def work(self, input_items, output_items):
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
                    self.mode = 0
            if pmt.symbol_to_string( tag.key ) == 'SO':
                eq_so = int( pmt.symbol_to_string( tag.value) )
                if eq_so == self.spectrum_occupancy:
                    print('Frames sind nun vollständig entzerrt!')
                    self.eq_so_true = 1
                    self.msc_sym = numpy.zeros(drm.msc_qam_cells[self.mode][self.spectrum_occupancy]-drm.msc_qam_cells_loss[self.mode][self.spectrum_occupancy]+2, dtype=numpy.complex64)
                    
                else:
                    # Nicht alle Modes implementiert
                    print( ' EQ hat falschen SO Wert! Wird neu g esendet... ')
                    self.spectrum_occupancy = -1
        
        # FAC
        self.get_fac_symbols(input_items[0])
        self.fac_decode()
        
        
        # Informationen zum Auslesen des SDC
        if self.fac_decoder.sdc_mode_qam != self.sdc_mod:
            self.sdc_mod = self.fac_decoder.sdc_mode_qam
        
        self.new_superframe = 0
        
        # SDC tritt nur im ersten Block eines Superframes auf
        if self.fac_decoder.identity == 0 or self.fac_decoder.identity == 3:
            # Überprüfen ob EQ schon voll läuft
            if self.eq_so_true:
                self.new_superframe    = 1
                self.msc_symbols_recvd = 0
                self.get_sdc_symbols(input_items[0])
                self.sdc_decode()
                


        # MSC 
            
        # Neu empfangene Multiplex Frames speichern
        if self.eq_so_true:
            # Vollständigen superframe in MSC Frames aufteilen
            if self.new_superframe and self.start_msc:
                self.n_rcvd_mux_frames += 3
                self.msc_mux_frames[0] = list( self.msc_mux_frames[3] )
                self.msc_mux_frames[1] = list( self.msc_mux_frames[4] )
                self.msc_mux_frames[2] = list( self.msc_mux_frames[5] )
                
                self.msc_mux_frames[3] = list( self.msc_mux_frames[6] )
                self.msc_mux_frames[4] = list( self.msc_mux_frames[7] )
                self.msc_mux_frames[5] = list( self.msc_mux_frames[8] )
                
                self.msc_mux_frames[6] = list( self.superframe[0:2337] )
                self.msc_mux_frames[7] = list( self.superframe[2337:2337*2] )
                self.msc_mux_frames[8] = list( self.superframe[2337*2:2337*3] )
                # Die letzten zwei dummy bits fallen automatisch weg
                
            
            # Neue Superframe symbole speichern
            for s in range(0, self.spf):
                for k in range(self.kmin, self.kmax+1):
                    if input_items[0][(s*1024)+(512+k)]  != 0 :
                        self.superframe[self.msc_symbols_recvd] = input_items[0][(s*1024)+(512+k)]
                        self.msc_symbols_recvd += 1
            
            
            #Sobald ein ganzer superframe empfangen wurde kann mit dem aufteilen der mux frame begonnen werden
            if self.msc_symbols_recvd == len(self.superframe):
                self.start_msc = 1
            
            # Sobald mehr als 5 Mux Frames empfangen wurden, kann mit dem Interleaven begonnen werden         
            if self.n_rcvd_mux_frames > 5:
                self.enough_mux_frames = 1

            #sobald 3 mux frames empfangen und interleavt wurden kann der msc decodiert werden
            if self.n_rcvd_mux_frames >= 7:
                self.start_msc_decode = 1

            
            # Sobald genug muxframes empfangen wurden kann der MSC Cell interleaver anfangen  zu arbeiten.                
            if self.start_msc_decode and self.new_superframe:
                #print('MSC Decoder läuft')
                self.msc_decell[0] = msc_dec.cell_interleaver( (self.msc_mux_frames[0:5]) ) 
                self.msc_decell[1] = msc_dec.cell_interleaver( (self.msc_mux_frames[1:6]) ) 
                self.msc_decell[2] = msc_dec.cell_interleaver( (self.msc_mux_frames[2:7]) ) 
                
                # Demodulation mapping auf 2 streams
                for frame in self.msc_decell:         
                    bits = msc_dec.qam_16_demod(frame)
                    # Interleaver pro stream
                    bits_0 = fac_dec.bit_deinterleaving(bits[0], 13)
                    bits_1 = fac_dec.bit_deinterleaving(bits[1], 21)
                    
                    bits_0 = msc_dec.dec_reform(bits_0, 1, 0)
                    bits_1 = msc_dec.dec_reform(bits_1, 1, 1)
                    
                    # Decoder pro stream
                    #print('\nDecode p 0')                    
                    msc_decoder = fac_dec.viterbi()
                    bits_0      = msc_decoder.decode(bits_0)
                    #print('Decode p 1')
                    msc_decoder = fac_dec.viterbi()
                    bits_1      = msc_decoder.decode(bits_1)
                    
                    
                    # Endzustand abschneiden [0,0,0,0,0,0]
                    bits_0 = bits_0[:-6]
                    bits_1 = bits_1[:-6]
                    
                    
                    # Repatitionierung, zusammenführen der streams
                    bits = msc_dec.departioning_of_information(bits_0, bits_1)
                    
                
                    # Energy Dispersal
                    bits = fac_dec.scrambler(bits)
                
                    # Crc, gibts nicht :'(
                    # Bei unserer Übertragung sollten allerdings die letzten 2 bits null sein
                    # und mit 0 gepadded um die nötige länge zu erreichen
                
                    bits = bits[0:-2]
                    
                    test_message = bits[-4*8:]
                    test_message = [int(x) for x in test_message]
                    self.text_massage.add_bits(test_message)
                    
                    audio_frame  = bits[0:-4*8]
                
            self.new_superframe = 0
            
        return len(input_items[0])
        
    def get_fac_symbols(self, sym_in):
        n = 0 
        symbol = 1
        self.fac_sym = [0] * 65
        #print(' INPUT ITEMS : ' + str(len(input_items[0])))
        # seh sehr gefährlich wegen leeren arrays die die reihenfolge zerlegen...
        for symbols in drm.fac_b:
            for carry in symbols:
                #print(str(n) + ' FAC INPUT : ' + str((symbol*1024)+(512+carry)) )
                self.fac_sym[n] = sym_in[(symbol*1024)+(512+carry)]
                # auf 0 setzen damit nachher nicht geprüft werden muss ob FAC oder nicht
                sym_in[(symbol*1024)+(512+carry)] = 0
                n  += 1
            symbol += 1
            
            
    def fac_decode( self ):        
        #Demodulation
        bits = fac_dec.qam_slicer(self.fac_sym)
        
        # Bit Deinterleaving
        bits = fac_dec.bit_deinterleaving(bits)               
        
        #Viterbi
        bits    = fac_dec.dec_reform(bits)
        decoder = fac_dec.viterbi()
        bits    = decoder.decode(bits)
        
        #Energy Dispersal
#        bits    = fac_dec.scrambler(bits[0:72])
        bits    = fac_dec.scrambler(bits[0:-6])
        
        # crc bits invertieren
        #crc = bits[64:72]
        crc     = [ int((x+1)%2) for x in bits[-8:]]
        bits    = [ int(x) for x in bits[0:-8]]
       
        if fac_dec.crc_check(bits+crc):
            self.fac_decoder.init(bits)
            if self.spectrum_occupancy != self.fac_decoder.spectrum_occupancy:
                self.spectrum_occupancy = self.fac_decoder.spectrum_occupancy
                self.kmin = drm.get_k_min(self.mode, self.spectrum_occupancy, 1)
                self.kmax = drm.get_k_max(self.mode, self.spectrum_occupancy, 1)
                
                # Tag an EQ senden
                msg = pmt.cons(pmt.string_to_symbol('SO'), pmt.string_to_symbol(str(self.spectrum_occupancy) ) )
                self.message_port_pub(pmt.intern('fac_out'), msg) 
                
                if self.show_fac_information:
                    self.fac_decoder.print_fac()
                    self.show_fac_information = 0
                    
                                     
                
        else:
            print( ' FAC CRC Fehler! ')
        

    ### SDC ###    
    def get_sdc_symbols(self, sym_in):
        '''liest alle SDC Symbole aus und speichert sie in einer Liste'''
        self.sdc_sym = []
        for symbol in range(0,2):
            for carry in range(self.kmin, self.kmax+1):
                if sym_in[(symbol*1024)+(512+carry)] != 0:
                    self.sdc_sym.append(sym_in[(symbol*1024)+(512+carry)])
                    # auf null setzen für leichte prüfung des MSC, theoretisch ist nach diesem Block nur noch MSC != 0
                    sym_in[(symbol*1024)+(512+carry)] = 0

        
        
        
            
    def sdc_decode( self ):        
        #Demodulation
        bits = fac_dec.qam_slicer(self.sdc_sym)
        
        # Bit Deinterleaving
        bits = fac_dec.bit_deinterleaving(bits)               
        # soweit sollte es identisch zum FAC sein
        
        #Viterbi
        bits    = sdc_dec.dec_reform(bits) # andere Punktierung? Code Rate 0.5 mit R0 = 0.5
        #viterbi ist wieder identisch
        decoder = fac_dec.viterbi()
        bits    = decoder.decode(bits)
        
        #Energy Dispersal
        #soweit so gut
        bits    = fac_dec.scrambler(bits[0:-6])
        
        # crc bits invertieren
        crc     = [ int((x+1)%2) for x in bits[-16:]]
        bits    = [ int(x) for x in bits[0:-16]]
        # 4 afs bits hinzufügen - WARUM???????? WARUM?????????
        bits    = [0,0,0,0] + bits
        if sdc_dec.crc_check(bits+crc):
             
            self.sdc_dec.init(bits)
            if self.show_sdc_information:
                self.sdc_dec.show_information()
                self.show_sdc_information = 0
            #print( ' SDC fehlerfrei empfangen!')                              
        else:
            print( ' SDC CRC Fehler! ')