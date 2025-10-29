k8055(N) / VM110(N)
=====
Velleman k8055(N) or VM110(N) linux driver and GUI sources built and tested .

![Velleman k8055 board](https://raw.github.com/rm-hull/k8055/master/k8055.jpg)



>"This software allows access to Velleman's K8055 card. This software was
developed to replace all other half-complete softwares for the k8055 board
under Linux. The library is made from scratch with the same functions as
described in Velleman's DLL usermanual. The command line tool is developed from
Julien Etelain and Edward Nys code.

>The reason for writing another driver for Linux was to get the debounce time to
work correctly. Nobody seemed to have figured out how it works (nor did
Velleman care to explain) so I studied it and have it working now with +-4%
accuracy of the actual settime. Note that the Velleman's DLL doesn't even get
this close.

>Another reason was to make it simple to use by writing a library for the k8055,
libk8055. Just by using "#include <k8055.h>" and compiling with "-lk8055" flags
you have access to all the functions described in Velleman's DLL documentation.

>The library is now also available in python, thanks to Pjetur G. Hjaltason.
Included with the source and some examples as well!

>Developer : Sven Lindberg <k8055@mrbrain.mine.nu> (python by Pjetur G.
Hjaltason <pjetur@pjetur.net>)"

# The package was adapted for linux kernel 6.1.0-40-amd64 and it may work on more recent kernels

How to build & install
----------------------
Install linux driver :

    $ sudo apt install build-essential libusb-1.0-0-dev
    $ cd driver/k8055
    $ sudo make 
    $ sudo make install

Install python3 wrapper:

cd pyk8055
sudo apt-get install python3-dev python3-setuptools swig
sudo python3 setup.py build
sudo python3 setup.py install
   

[GPL](http://www.gnu.org/licenses/gpl.html)

References
----------
* http://www.velleman.eu/products/view/?country=be&lang=en&id=351346

* http://www.velleman.eu/downloads/0/user/usermanual_k8055_dll_uk.pdf

* http://george-smart.co.uk/wiki/Nokia_3310_LCD

* https://sites.google.com/site/vellemank8055/

* http://www.robert-arnold.de/cms/en/2010/10/zugriff-fur-nicht-root-user-auf-usb-board-k8055-unter-ubuntu-9-10-erlauben/

