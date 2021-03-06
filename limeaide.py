#!/bin/python

import sys, os, argparse, getpass
from datetime import datetime
from session import Session
from client import Client
from deploy_lime import LimeDeploy
from deploy_volatility import VolDeploy


class Limeaide(object):
    """Deploy LiME LKM to remote host in order to scrape RAM"""

    _version = "1.2.3"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'
        self.args_case = ''
        self.args_clean = False
        self.args_volatility = True

    def check_tools(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        if not os.path.isdir(self.lime_dir):
            if not os.path.isdir(self.tools_dir):
                os.mkdir(self.tools_dir)
            sys.exit("Please download LiME and place in the ./tools/ dir")

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("remote", help="remote host IP")

        parser.add_argument("-s", "--sudoer", help="use a sudo user instead default: root")
        parser.add_argument("-o", "--output", help="name the outputfile")
        parser.add_argument("-C", "--dont-compress", action="store_true",
                help="Do NOT compress dump into Bzip2 format")
        parser.add_argument("-V", "--no-profile", action="store_true",
                help="Do NOT create volatility profile")
        parser.add_argument("-c", "--case", help="Append case number to output dir")
        parser.add_argument("--force-clean",  action="store_true",
                help="Force clean client after failed deployment")
        parser.add_argument("--version",  action="store_true",
                help="Version information")

        return parser.parse_args()

    def get_client(self, args):
        client = Client()
        client.ip = args.remote
        if args.sudoer != None:
            client.user = args.sudoer
            client.is_sudoer = True

        if args.output != None:
            client.output = args.output

        if args.dont_compress:
            client.compress = not client.compress

        if args.no_profile:
            self.args_volatility = not self.args_volatility

        if args.case != None:
            self.args_case = 'case_%s' %args.case

        if args.force_clean:
            self.args_clean = args.force_clean

        if args.version:
            sys.exit(_version)

        return client

    def main(self):
        print("""\
            .---.                                                     _______
            |   |.--. __  __   ___         __.....__              .--.\  ___ `'.         __.....__
            |   ||__||  |/  `.'   `.   .-''         '.            |__| ' |--.\  \    .-''         '.
            |   |.--.|   .-.  .-.   ' /     .-''"'-.  `.          .--. | |    \  '  /     .-''"'-.  `.
            |   ||  ||  |  |  |  |  |/     /________\   \    __   |  | | |     |  '/     /________\   |
            |   ||  ||  |  |  |  |  ||                  | .:--.'. |  | | |     |  ||                  |
            |   ||  ||  |  |  |  |  |\    .-------------'/ |   \ ||  | | |     ' .'\    .-------------'
            |   ||  ||  |  |  |  |  | \    '-.____...---.`" __ | ||  | | |___.' /'  \    '-.____...---.
            |   ||__||__|  |__|  |__|  `.             .'  .'.''| ||__|/_______.'/    `.             .'
            '---'                        `''-...... -'   / /   | |_   \_______|/       `''-...... -'
                                                         \ \._,\ '/
                                                          `--'  `"
             by kd8bny v%s \n""" %(self._version))
        print("LiMEaide is licensed under GPL-3.0\nLiME is licensed under GPL-2.0\n")

        self.check_tools()
        args = self.get_args()
        client = self.get_client(args)

        print("Attempting secure connection %s@%s" %(client.user, client.ip))
        client.pass_ = getpass.getpass()
        session = Session(client)

        if not self.args_clean:
            client.output_dir = "%s%s%s/" %(self.output_dir, self.args_case,
                    datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f"))

            os.mkdir(client.output_dir)
            LimeDeploy(session).main()
            print("Memory extraction is complete\n\n%s is in %s"
                    %(client.output, client.output_dir))

            if self.args_volatility:
                VolDeploy(session).main()
                print("Profile generated")

        session.clean()
        sys.exit("Clean attempt complete")

if __name__ == '__main__':
    Limeaide().main()
