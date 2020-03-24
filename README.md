# Bug Scanner

Bug Scanner for Internet Freedom


Subdomain Scanner or Finder
---------------------------

- [subfinder](https://github.com/projectdiscovery/subfinder) (golang)
- [findomain](https://github.com/Edu4rdSHL/findomain) (rust)


Install
-------

    $ git clone https://github.com/aztecrabbit/bugscanner
    $ cd bugscanner
    $ python3 -m pip install -r requiremets.txt --user
    $ python3 setup.py install --user


Usage
-----

**subdomain scanner or finder**

    $ subfinder -d bug.com -o bug.com.txt

or

    $ findomain -o -t bug.com


**run**

    $ bugscanner bug.com.txt


