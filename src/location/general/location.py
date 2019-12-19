import sys
import os
import json
from commands import getoutput, getstatusoutput
import requests



try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def get_signal_strengths(wifi_scan_method):
    wifi_data = []

    # GNU/Linux
    if wifi_scan_method is 'iw':
        iw_command = 'iw dev %s scan' % (args.wifi_interface)
        iw_scan_status, iw_scan_result = getstatusoutput(iw_command)

        if iw_scan_status != 0:
            print "[!] Unable to scan for Wi-Fi networks !"
            print "Used command: '%s'" % iw_command
            print "Result:\n" + '\n'.join(iw_scan_result.split('\n')[:10])
            if len(iw_scan_result.split('\n')) > 10:
				print "[...]"
            exit(1)
        else:
            parsing_result = re.compile("BSS ([\w\d\:]+).*\n.*\n.*\n.*\n.*\n\tsignal: ([-\d]+)", re.MULTILINE).findall(iw_scan_result)

            wifi_data = [(bss[0].replace(':', '-'), int(bss[1])) for bss in parsing_result]

    # Mac OS X
    elif wifi_scan_method is 'airport':
        address_match = '([a-fA-F0-9]{1,2}[:|\-]?){6}'  # TODO useless ?
        airport_xml_cmd = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport --scan -x'
        airport_scan_status, airport_scan_xml = getstatusoutput(airport_xml_cmd)

        if airport_scan_status != 0:
            print "[!] Unable to scan for Wi-Fi networks !"
            print "Used command: '%s'" % airport_xml_cmd
            print "Result:\n" + '\n'.join(airport_scan_xml.split('\n')[:10])
            if len(airport_scan_xml.split('\n')) > 10:
				print "[...]"
            exit(1)
        else:
            try:
            	root = ET.fromstring(airport_scan_xml)
            	networks = root.getchildren()[0]
            except Exception as e:
            	print e
            

            wifi_data = [(network.find("string").text, abs(int(network.findall("integer")[7].text))) for network in networks]

    # OpenBSD
    elif wifi_scan_method is 'ifconfig':
        ifconfig_cmd = 'ifconfig %s scan' % (args.wifi_interface)
        ifconfig_scan_status, ifconfig_scan_result = getstatusoutput(ifconfig_cmd)

        if ifconfig_scan_status != 0:
            print "[!] Unable to scan for Wi-Fi networks !"
            print "Used command: '%s'" % ifconfig_cmd
            print "Result:\n" + '\n'.join(ifconfig_scan_result.split('\n')[:10])
            if len(ifconfig_scan_result.split('\n')) > 10:
				print "[...]"
            exit(1)
        else:
            parsing_result = re.compile("nwid\s+[\w-]+\s+chan\s+\d+\s+bssid\s+([\w\d\:]+)\s+([-\d]+)dBm", re.MULTILINE).findall(ifconfig_scan_result)

            wifi_data = [(bss[0].replace(':', '-'), int(bss[1])) for bss in parsing_result]

    return wifi_data


def check_prerequisites():
    # Moved arguments check and parsing to get_arguments()

    # Do something/nothing here for different kind of systems
    if sys.platform.startswith(('linux', 'netbsd', 'freebsd', 'openbsd')) or sys.platform == 'darwin':
        wifi_scan_method = None
        perm_cmd = None

        # Do something specific to GNU/Linux
        if sys.platform.startswith('linux'):
            print "linux"
            # If not launched with root permissions
            if os.geteuid() != 0:
                # First try with 'sudo'
                which_sudo_status, which_sudo_result = getstatusoutput('which sudo')
                # If 'sudo' is installed and current user in 'sudo' group
                if which_sudo_status is 0:
                    # Like in the ubuntu default sudo configuration
                    # "Members of the admin group may gain root privileges"
                    # "Allow members of group sudo to execute any command"
                    current_user_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
                    if 'sudo' in current_user_groups or \
                       'admin' in current_user_groups:
                        perm_cmd = 'sudo --preserve-env'
                    #etc_sudoers_status, etc_sudoers_result = getstatusoutput('sudo cat /etc/sudoers')
                    # If 'sudo' is configured for the current user
                    #if etc_sudoers_status is 0:
                        #perm_cmd = 'sudo'
                # If not 'sudo'
                if perm_cmd is None:
                    # Check other methods for getting permissions
                    for su_gui_cmd in ['gksu', 'kdesu', 'ktsuss', 'beesu', 'su -c', '']:
                        which_cmd_status, which_cmd_result = getstatusoutput('which '+su_gui_cmd.split()[0])
                        # If one is found, keep it in 'su_gui_cmd' var
                        if which_cmd_status is 0:
                            break
                    # If 'su_gui_cmd' var is not empty, we have one !
                    if su_gui_cmd:
                        perm_cmd = su_gui_cmd
                    else:
                        print "Error: this script need to be run as root !"
                        exit(1)
            #else:
                #print "[+] Current user is '%s'" % os.environ.get('USER')

            # Command available to ask permissions
            if perm_cmd:
                # Restart as root
                #print "[+] This script need to be run as root, current user is '%s'" % os.environ.get('USER')
                if args.verbose:
                    print "[+] Using '" + perm_cmd.split()[0] + "' for asking permissions"
                if perm_cmd is 'sudo --preserve-env':
                    #print perm_cmd.split()[0], perm_cmd.split() + [
                    #          ' '.join(['./' + sys.argv[0].lstrip('./')])
                    #      ] + sys.argv[1:]
                    os.execvp(perm_cmd.split()[0], perm_cmd.split() + [
                                  ' '.join(['./' + sys.argv[0].lstrip('./')])
                              ] + sys.argv[1:])
                else:
                    #print perm_cmd.split()[0], perm_cmd.split() + [
                    #          ' '.join(['./' + sys.argv[0].lstrip('./')] + sys.argv[1:])
                    #      ]
                    os.execvp(perm_cmd.split()[0], perm_cmd.split() + [
                                  ' '.join(['./' + sys.argv[0].lstrip('./')] + sys.argv[1:])
                              ])

            which_iw_status, which_iw_result = getstatusoutput('which iw')
            if which_iw_status != 0:
                print "Missing dependency: 'iw' is needed\n" + \
                      "    iw - tool for configuring Linux wireless devices"
                if 'ubuntu' in getoutput('uname -a').lower():
                    print "    > sudo apt-get install iw"
                # TODO for other distro, see with /etc/*release files ?
                elif 'gentoo' in getoutput('cat /etc/*release').lower():
                    print "    > su -c 'emerge -av net-wireless/iw'"
                exit(1)
            else:
                wifi_scan_method = 'iw'

        # Do something specific to Mac OS X
        elif sys.platform == 'darwin':
            print "Mac OS X"
            aiport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
            if not os.path.exists(aiport_path):
                print "Missing dependency:\n" + \
                      "    airport - tool for configuring Apple wireless devices from Terminal.app"
                exit(1)
            else:
                wifi_scan_method = 'airport'

        # Do something specific to OpenBSD
        # TODO test with NetBSD and FreeBSD
        elif sys.platform.startswith(('netbsd', 'freebsd', 'openbsd')):
            print "BSD"
            # See: http://man.openbsd.org/su.1

            # If the optional shell arguments are provided on the command line, they are passed to the login shell
            # of the target login. This allows it to pass arbitrary commands via the -c option as understood by most
            # shells. Note that -c usually expects a single argument only; you have to quote it when passing multiple
            # words.

            # If group 0 (normally "wheel") has users listed then only those users can su to "root". It is not
            # sufficient to change a user's /etc/passwd entry to add them to the "wheel" group; they must explicitly
            # be listed in /etc/group. If no one is in the "wheel" group, it is ignored, and anyone who knows the root
            # password is permitted to su to "root".

            # If not launched with root permissions
            if os.geteuid() != 0:
                # Try with 'su -c' if current user in 'wheel' group
                # Like in the OpenBSD default su configuration
                # "If group 0 (normally "wheel") has users listed then only those users can su to "root"."
                # "If no one is in the "wheel" group, it is ignored [...]"
                current_user_groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
                if 'wheel' in current_user_groups:
                    perm_cmd = 'su -c'
                else:
                    # TODO "If no one is in the "wheel" group, it is ignored [...]" ?
                    print "Error: this script need to be run as root !"
                    exit(1)

            wifi_scan_method = 'ifconfig'

    else:
        # All other systems - or exception for non-supported system
        # Like 'win32'...
        # TODO is 'cygwin' could be found on Mac OS X operation systems ?
        print "Error: unsupported operating system..." + \
              "\nMicrosoft Windows operating systems are not currently supported, missing Wi-Fi cli tool / library." + \
              "\nIf you use a Mac OS X operating system, the detected plateform could have been 'cygwin'," + \
              "\nplease let us know so we can publish a correction with your help !"
        exit(1)

    return wifi_scan_method




with open('settings.json') as f:
	settings = json.load(f)

API_KEY = settings["api_key"]

# Checking permissions, operating system and software dependencies
wifi_scan_method = check_prerequisites()
try:
	wifi_data = get_signal_strengths(wifi_scan_method)
	data = {
		'considerIp': False,
		'wifiAccessPoints':[
			{
				"macAddress": mac,
				"signalStrength": signal
			} for mac, signal in wifi_data]
	}
except:
	data = {
		'considerIp': True,
		'wifiAccessPoints':[]
	}

headers = {"Content-Type": "application/json"}
url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + settings["api_key"]
#url = "https://location.services.mozilla.com/v1/geolocate?key=" + settings["api_key"]
response = requests.post(url, headers=headers, data=json.dumps(data))
googleLocation = json.loads(response.content) 

with open('location.json') as f:
	location = json.load(f)

location["location"]["lat"] = googleLocation["location"]["lat"]
location["location"]["lng"] = googleLocation["location"]["lng"]
location["accuracy"] = googleLocation["accuracy"]

with open('location.json', 'w') as output:
	json.dump(location, output, indent=4)


