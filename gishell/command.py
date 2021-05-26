
from cmd import Cmd
import argparse
from operator import attrgetter
from datetime import datetime

from arcgis import GIS

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box




parser = argparse.ArgumentParser(description='ArcGIS Online/Portal Command Line Tool')
parser.add_argument("-url", "--url", default='https://bob.maps.arcgis.com', type=str, help='ArcGIS URL for the Organization')
parser.add_argument("-u", "--username", default='bob', type=str, help='ArcGIS Online Username')
parser.add_argument("-p", "--password", default='password123', type=str, help='ArcGIS Online Password')
parser.add_argument("-pf", "--profile", default='', type=str, help='ArcGIS Online Profile *Stored Locally*')
parser.parse_args()


console = Console(width=120)


messages = {
    'helpmsg': """
    """,
    'welcome': """
[bold blue]Welcome to the GIShell Command Line Tools[/]

Type help or ? to list the available commands  
Type login to begin using this application
""",
    'profile_info': """
Profiles can be used to store and retrieve your login credentials from your local OS credential storage.  
When you login via this app (or using the standalone API) all you will need to provide is the profile name.  
*No confidential information is stored by this application.*   

""",
    'profile': """
Please provide a name for this profile. Using greater than 3 letters, numbers and hyphens(only).  
Save this profile name to login via this app in the future.    

    """,
    'exit': """""",
    'login_msg': """
    [blue]Welcome[/] {}!
    [blue]Username:[/] {}
    [blue]Organization Name:[/] {}
    [blue]Last Login at:[/] {}
    """,
    'user_details': """
User Details

Name: {}
Username: {}
Email: {}
Organization: {}
Organization Role: {}
Date Created: {}
Date Modified: {}
Last Login: {}
Multifactor Auth Enabled: {}
Local Working Directory: {}
UserID: {}
OrgID: {}

Storage Used: {}
Storage Available: {}
User Description: {}

    """,
    '': """""",
    '': """""",
    '': """""",
    '': """""",
    '': """""",
    '': """""",
}


def convert_time(api_time):
    return datetime.fromtimestamp(api_time/1000).strftime('%a %m/%d/%Y at %I:%M %p')


class GIShell(Cmd):
    prompt = '(GIShell): '
    intro = """"""
    session = None

    def do_exit(self, input=None):
        """Does this qualify?"""
        console.print("[bold blue]Goodbye![/]")
        return True

    def do_me(self, input):
        user = self.session.users.me
        org = self.session.properties
        console.print(messages['user_details'].format(
            user['fullName'],
            user['username'],
            user['email'],
            org.name,
            user['role'],
            convert_time(self.session.users.me['created']),
            convert_time(self.session.users.me['modified']),
            convert_time(self.session.users.me['lastLogin']),
            user['mfaEnabled'],
            user._workdir,
            user['id'],
            user['orgId'],
            user['storageUsage'],
            user['storageQuota'],
            user['description']
        ), justify='left')

    def do_user(self, input):
        """
        User Related Commands
        :param input: if blank it uses the current user. If used a 'user:<input>' search is issued.
        :return:
        """
        org = self.session.properties
        if input:
            user = self.session.users.get(input)
            if not user:
                return console.print('Username: {} not found'.format(input))
        else:
            user = self.session.users.me
        console.print(messages['user_details'].format(
            user['fullName'],
            user['username'],
            user['email'],
            org.name,
            user['role'],
            convert_time(self.session.users.me['created']),
            convert_time(self.session.users.me['modified']),
            convert_time(self.session.users.me['lastLogin']),
            user['mfaEnabled'],
            user._workdir,
            user['id'],
            user['orgId'],
            user['storageUsage'],
            user['storageQuota'],
            user['description']
        ), justify='left')

    def do_local(self, input):
        pass

    def do_profile(self, input):
        pass

    def do_group(self, input):
        pass

    def do_login(self, input):
        """
        Logs the user into the intended GIS Server
        :param input:
        :return:
        """
        # TODO: check if any profiles currently exist for the user and ask if one should be used.
        # TODO: Check if no profiles then prompt to create one.
        console.print('\n')
        console.print(messages['profile_info'], justify='center')
        profilechk = Confirm.ask("\nWould you like to define a profile?")

        if profilechk:
            console.print(messages['profile'])
            profile = Prompt.ask('Profile Name')

        def cred_check():
            def cred_prompt():
                console.print("\nPlease provide the details of your ArcGIS account.\n")
                url = Prompt.ask("ArcGIS URL")
                username = Prompt.ask("Username")
                password = Prompt.ask("Password", password=True)
                return url, username, password

            def cred_confirm(crd):
                confirm = Confirm.ask("""You have provided the following:
            URL: {}
            Username: {}                                   
            Password: {}
            Is this correct?""".format(*crd))
                return confirm
            cred = cred_prompt()

            if not cred_confirm(cred):
                exit_chk = Confirm.ask("Do you wish to exit?")
                if exit_chk:
                    return None
                else:
                    cred_check()
            else:
                return cred
        credentials = cred_check()
        if not credentials:
            return

        else:
            try:
                # TODO: fix this mess. Need to handle all sorts of exceptions here
                connection = GIS(url=credentials[0], username=credentials[1], password=credentials[2])
                self.session = connection
                return console.print(messages['login_msg'].format(
                    self.session.users.me["fullName"],
                    self.session.users.me["username"],
                    self.session.properties.name,
                    convert_time(self.session.users.me['lastLogin'])
                ), style="magenta")

            except:
                return console.print(ConnectionError.mro(), style="Red Underline Bold")

    def do_content(self, input):
        """
        Perform a search of the available content at the Feature Layers level.
        Searches should be formatted in the following format. '<field>:<search>'

        eg. 'owner:bob*'
        (Wildcards are allowed)

        Reference: https://developers.arcgis.com/rest/users-groups-and-items/search-reference.htm
        Available search terms for

        :param string input: If no input is used then it returns all layers within the current users organization.
                      If an input is used then it will search all of the default search terms for the input.
                      ("title", "tags", "snippet", "description", "type", "typekeywords")

        :return list: List of Feature Layers
        """
        if input:
            search = self.session.content.search(query=input)
        else:
            query = Prompt.ask("Would you like to query for a layer?",
                               choices=[
                                   "title", "tags", "description", "type", "owner", "any", "all", "no"
                               ],
                               default="title"
                               )
            console.print(query+"  HA! this doesnt work yet silly.")
        search = self.session.content.search(query="")

        table = Table(title="AGOL Layers", caption="Number of Layers: {}".format(len(search)), width=120,
                      title_style='Bold Underline Red', caption_style="Bold cyan", box=box.SIMPLE, border_style='blue')

        table.add_column("Item Number", justify="center", style="yellow", header_style="yellow")
        table.add_column("Title", justify="center", style="cyan", header_style="cyan")
        table.add_column("Type", justify="center", style="blue", header_style="blue")
        table.add_column("Num Layers", justify="center", style="purple", header_style="purple")
        table.add_column("Owner", justify="center", style="green", header_style="green", no_wrap=True)
        table.add_column("Tags", justify="center", style="white", header_style="white")
        table.add_column("Description", justify="center", style="red", header_style="red")


        if search:
            for count, item in enumerate(sorted(search, key=attrgetter('type', 'owner', 'title')), 1):
                if item._has_layers():
                    lyrs = str(len(item.layers))
                else:
                    lyrs = 'None'
                table.add_row(str(count),
                              item.title,
                              item.type,
                              lyrs,
                              item.owner,
                              str([tag for tag in item.tags]),
                              item.description
                              )

            console.print(table)
        else:
            console.print("No results!", style="bold red")


# console.print('\n')
# INTRO AND HELP
console.rule("[bold magenta]GIShell - Cloud GIS Management[/]", style='blue')
console.print(messages['welcome'], style='white', justify='center')
GIShell().cmdloop()

