#### system deps
~~~
- python3
- python3-dbus
- hciconfig         [bluez-deprecated]
- libhidapi-hidraw0
- hidapi-devel
~~~

#### Cursed Bluetooth Hardware
[https://github.com/Poohl/joycontrol/issues/4](https://github.com/Poohl/joycontrol/issues/4)

#### Create virtual enviroment
~~~
$ python3 -m venv env
$ source source env/bin/activate
~~~

#### Install deps python 3
~~~
$ pip install aioconsole hid dbus-python crc8
~~~

#### install joycontrol
~~~
$ git clone https://github.com/Poohl/joycontrol
$ pip install ./joycontrol
~~~

#### NINTENDO SWITCH
~~~
- version 12.1.0
- version 13.0.0
~~~

#### RUN DEMO
~~~
$ sudo -E env PATH=$PATH python joytransfer.py
~~~

#### DEMO IN YOUTUBE
[https://www.youtube.com/watch?v=GBxLCyi0jz8](https://www.youtube.com/watch?v=GBxLCyi0jz8) 

#### FIXME, connect joycon after sync cause disconnection
[https://www.youtube.com/watch?v=XbHErgeM34E](https://www.youtube.com/watch?v=XbHErgeM34E) 
