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

Scan using regular quota

    $ ~/go/bin/subfinder -d bug.com -o bug.com.txt

**Bug Scanner**

Scan only when using the website quota you want to scan

`--mode direct --port 80`

    $ bugscanner bug.com.txt

<!-- -->

    $ bugscanner bug.com.txt --port 443

`--mode ssl --deep 2`

    $ bugscanner bug.com.txt --mode ssl

<!-- -->

    $ bugscanner bug.com.txt --mode ssl --deep 3

`--mode proxy --port 80`

    $ bugscanner bug.com.txt --mode proxy --proxy proxy.example.com:8080

<!-- -->

    $ bugscanner bug.com.txt --mode proxy --proxy proxy.example.com:8080 --port 443


Updating
--------

    $ python3 -m pip install --upgrade bugscanner


Note
----

- `--mode direct` for [brainfuck psiphon pro go](https://github.com/aztecrabbit/brainfuck-psiphon-pro-go)
- `--mode ssl` for server name indication [brainfuck tunnel shadowsocks](https://github.com/aztecrabbit/brainfuck-tunnel-shadowsocks)
- `--mode ssl --deep n` is like this (cdn.bug.example.com : deep 2 = example.com, deep 3 = bug.example.com, etc)
- `--mode proxy` for [brainfuck tunnel go](https://github.com/aztecrabbit/brainfuck-tunnel-go) or [brainfuck tunnel openvpn](https://github.com/aztecrabbit/brainfuck-tunnel-openvpn)

