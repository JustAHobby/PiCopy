# PiCopy
Python code using tkinter GUI to allow for file copies between storage devices on the RaspberryPi 

Raspbian with Touchscreen support:
https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install


Other Installs:
http://effbot.org/tkinterbook/tkinter-index.htm
sudo apt-get install python-tk

http://www.pythonforbeginners.com/modules-in-python/how-to-use-sh-in-python
sudo pip install sh 

https://www.raspberrypi.org/forums/viewtopic.php?f=28&t=45607
sudo apt-get install exfat-fuse exfat-utils

https://raspberrypi.stackexchange.com/questions/43477/can-not-make-directory-on-my-usb-disk-connected-raspberry-pi-2
sudo apt-get install ntfs-3g
fdisk -l (used to find file path of ntfs drive)
mount -t ntfs-3g <dir path fdisk gives> <custom dir in /media/pi/>
