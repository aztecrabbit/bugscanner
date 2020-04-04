# Bug Scanner

Bug Scanner for Internet Freedom


Sub Finder
----------

- [subfinder](https://github.com/projectdiscovery/subfinder) (golang)


Install
-------

**Sub Finder**

    $ go get -v -u github.com/projectdiscovery/subfinder/cmd/subfinder

**Bug Scanner**

    $ python3 -m pip install bugscanner

or

    $ git clone https://github.com/aztecrabbit/bugscanner
    $ cd bugscanner
    $ python3 -m pip install -r requirements.txt
    $ python3 setup.py install


Usage
-----

**Sub Finder**

    $ ~/go/bin/subfinder -d bug.com -o bug.com.txt

**Bug Scanner**

    $ bugscanner bug.com.txt


