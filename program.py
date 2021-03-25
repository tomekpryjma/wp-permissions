import sys
import argparse
import os
import pwd
from verbose import Verbose

class Program:
    def __init__(self):
        self.args = self.init()
        self.v = Verbose(self.args.verbose)
        self.dir_octal = 0o0755
        self.file_octal = 0o0644
    
    def init(self):
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
            return parser.parse_args()
        except IOError as err:
            self.exit_program(err)

    def exit_program(self, msg):
        print(msg)
        sys.exit(2)

    def chown(self, path, uid, gid):
        self.v.print("chown: " + path)
        os.chown(path, uid, gid)

    def chmod(self, path, octal):
        self.v.print("chmod: " + path)
        os.chmod(path, octal)

    def get_uids(self):
        try:
            admin_user_uid = pwd.getpwnam(self.args.admin_user).pw_uid
            web_user_uid = pwd.getpwnam(self.args.web_user).pw_uid
        except KeyError as err:
            self.exit_program(err)

        return [admin_user_uid, web_user_uid]

    def recursive_ownership_and_permission_change(self, sitepath, uid, gid):
        for root, dirs, files in os.walk(sitepath):
            for d in dirs:
                dir_path = os.path.join(root, d)
                self.chown(dir_path, uid, gid)
                self.chmod(dir_path, self.dir_octal)
            for f in files:
                file_path = os.path.join(root, f)
                self.chown(file_path, uid, gid)
                self.chmod(file_path, self.file_octal)

        self.chown(sitepath, uid, gid)
        self.chmod(sitepath, self.dir_octal)

    def strict_permissions(self, sitepath):
        wp_content_dir = sitepath + "wp-content"
        themes_dir = sitepath + "wp-content/themes"

        uids = self.get_uids()
        self.recursive_ownership_and_permission_change(sitepath, uids[0], uids[0])

        if os.path.isdir(wp_content_dir):
            self.recursive_ownership_and_permission_change(wp_content_dir, uids[1], uids[1])

        if os.path.isdir(themes_dir):
            self.recursive_ownership_and_permission_change(themes_dir, uids[0], uids[0])


    def lax_permissions(self, sitepath):
        uids = self.get_uids()
        git_dir = sitepath + ".git"
        gitignore = sitepath + ".gitignore"
        self.recursive_ownership_and_permission_change(sitepath, uids[1], uids[1])

        if os.path.isdir(git_dir):
            self.recursive_ownership_and_permission_change(git_dir, uids[0], uids[0])
            
        if os.path.isfile(gitignore):
            self.chown(gitignore, uids[0], uids[0])
            self.chmod(gitignore, self.file_octal)

    def run(self):
        self.args.webroot = self.args.webroot.rstrip("/") + "/"
        self.args.siteroot = self.args.siteroot.lstrip("/")
        self.args.siteroot = self.args.siteroot.rstrip("/") + "/"

        if not os.path.isdir(self.args.webroot):
            self.exit_program("The specified webroot does not exist: " + self.args.webroot)

        for directory in os.listdir(self.args.webroot):
            if directory.startswith("."): continue

            sitepath = self.args.webroot + directory + "/" + self.args.siteroot

            if not os.path.isdir(sitepath):
                self.v.print("The specified sitepath does not exist: " + sitepath)
                continue

            if not os.path.isdir(sitepath + "wp-admin"): # Check if directory uses WordPress
                self.v.print(directory + " does not use WordPress, skipping...")
                continue
            
            if self.args.level == 1:
                self.strict_permissions(sitepath)
            elif self.args.level == 2:
                self.lax_permissions(sitepath)