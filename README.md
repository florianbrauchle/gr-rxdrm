DRM Empfängerblöcke für GNURadio

## Abhändigkeiten
gnuradio
boost

pkgconfig
gnuradio dev
boost dev


## Installation

```
mkdir build
cd build
cmake ..
make
sudo make install
```

## Probleme
Modul wird in /usr/local/ installiert und nicht in /usr/...
Das Modul wird nicht gefunden, da nicht alle GNU Radio-Versionen in diesem Ordner suchen. Startet man den GNU-Radio-Companion aus der Konsole, so werden die Blockpfade angezeigt.
Um einen Pfad einzufügen muss die Variable GRC_BLOCK_PATH mit folgendem Befehl geändert werden.

```
export GRC_BLOCKS_PATH=/usr/local/share/gnuradio/grc/blocks:$GRC_BLOCKS_PATH
```
