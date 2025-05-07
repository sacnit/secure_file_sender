# This needs to be the combination of both files, maybe just fucking passing shit to both files
import argparse
import ultrapeer as up
import leaf as l

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Twisted TUI Client",
        description="A Twisted client with an interactive terminal interface."
    )
    parser.add_argument("-U", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Server host address (default: 127.0.0.1)")
    parser.add_argument("-P", "--port", dest="port", type=int, default=9999,
                        help="Server port number (default: 9999)")
    parser.add_argument("-C", "--certificate", dest="certificate", type=str, default="",
                        help="Directory containing certificate `cert.crt` and key `key.key`")
    parser.add_argument("-UP", "--ultrapeer-port", dest="uport", type=int, default=4443,
                        help="Server port number (default: 4443)")
    parser.add_argument("-J", "--join", dest="join", default=False,
                        help="Should the ultrapeer specified be joined (default: False)")
    parser.add_argument("-F", "--forest-port", dest="fport", type=int, default=4444,
                        help="Port number to use for syncing with the forst (default: 4444)")
    parser.add_argument("-M", "--mode", dest="mode", default="leaf",
                        help="which mode to run in `leaf` or `ultrapeer` (default: leaf)")
    args = parser.parse_args()
    
    ultrapeer = args.ultrapeer
    uport = args.uport
    join = args.join
    port = args.port
    fport = args.fport
    certificate = args.certificate
    mode = args.mode
    
    if mode == "leaf":
        l.main(ultrapeer, port, certificate)
    elif mode == "ultrapeer":
        up.main(ultrapeer, uport, join, port, fport, certificate)
    else:
        parser.print_help()