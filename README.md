# agilent-rs232
A basic script to read the waveform from an Agilent 54621A (Note: Has also been checked with 54622D) oscilloscope via RS232 and display it using matplotlib.

It can convert this:

![scope](scope.jpg?raw=true "Oscilloscope reading")

To this:

![matplotlib](reading.png?raw=true "Matplotlib rendering")

I wrote a blog post to go along with this! You can find it [here](https://01001000.xyz/2020-05-07-Walkthrough-Agilent-Oscilloscope-RS232/)!

# Usage

The program is written in python3.

```
usage: agilent-rs232.py [-h] [--port PORT] [--baud BAUD] [--channel CHANNEL]
                        [--length LENGTH]

optional arguments:
  -h, --help            show this help message and exit
  --port PORT, -p PORT  set serial port (default /dev/ttyUSB0)
  --baud BAUD, -b BAUD  set serial baud rate (default 57600)
  --channel CHANNEL, -c CHANNEL
                        set probe channel (default 1)
  --length LENGTH, -l LENGTH
                        number of samples (default 1000)
```

# Other implementations

I'm not the first person to want to solve this problem! 
Although I did not use their code, a more full-featured approach to reading scopes and other tools from Python can be found under the [PyVisa](https://pyvisa.readthedocs.io/en/latest/) library.
