import sys
import argparse
import os
from verbose import Verbose

# /home/tomek-dev/projects/testing/wp-updates-prep/srv

def exit_program(msg):
    print(msg)
    sys.exit(2)    

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", "-d", action="store", dest="domain", help="If left blank, permissions will run on all domains in the webroot", type=str, default=False)
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all actions taken by this script")

    required = parser.add_argument_group("required arguments")
    required.add_argument("--webroot", "-w", action="store", dest="webroot", help="Set the webroot of where all the domain directories exist, e.g. /var/www/html", type=str, required=True)
    required.add_argument("--siteroot", "-s", action="store", dest="siteroot", help="Set the siteroot of that all the domains share, e.g. public/html", type=str, required=True)
    required.add_argument("--web-user", "-b", action="store", dest="web_user", help="Set the username of the webserver, e.g. www-data", type=str, required=True)
    required.add_argument("--admin-user", "-a", action="store", dest="admin_user", help="Set the username of your user", type=str, required=True)
    required.add_argument("--level", "-l", action="store", dest="level", help="Set strictness level", type=int, required=True)

    try:
        args = parser.parse_args()
    except IOError as err:
        parser.error(str(err))
        sys.exit(2)

    v = Verbose(args.verbose)
    args.webroot = args.webroot.rstrip("/") + "/"
    args.siteroot = args.siteroot.lstrip("/")
    args.siteroot = args.siteroot.rstrip("/") + "/"

    if not os.path.isdir(args.webroot):
        exit_program("The specified webroot does not exist: " + args.webroot)

    for directory in os.listdir(args.webroot):
        if directory.startswith("."): continue

        sitepath = args.webroot + directory + "/" + args.siteroot

        if os.path.isdir(sitepath + "wp-admin"): # Check if directory uses WordPress
            v.print(directory + " does not use WordPress, skipping...")
            continue
        


if __name__ == "__main__":
    main(sys.argv)