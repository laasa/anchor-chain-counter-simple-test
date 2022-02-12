# anchor-chain-counter-test
simple test to find out how avnav plugins work

![grafik](https://user-images.githubusercontent.com/98450191/153688239-e35b59e5-1980-4b45-a585-1cdbda22e37e.png)


It is widely based on the more nmea plugin => https://github.com/kdschmidt1/avnav-more-nmea-plugin).

# Software installation

To install this plugin please 
- install packages via: sudo apt-get update && sudo apt-get install pigpio python-pigpio python3-pigpio
- create directory '/usr/lib/avnav/plugins/anchor-chain-counter-test' and 
- and copy the files anchorChainReader.py and plugin.py to this directory.

# Using in anvav

![grafik](https://user-images.githubusercontent.com/98450191/153617899-a929aa98-2876-42d8-be1e-c32a032bc04b.png)


# How to test
simply call
- python /usr/lib/avnav/plugins/anchor-chain-counter-test/anchorChainReader.py
- the anchor chain value in avnav should increase from 0 upto 10.0 in 50 seconds
