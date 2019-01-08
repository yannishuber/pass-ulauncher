""" Yannis Huber 2019 """

from subprocess import check_output
from os import path as os_path
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

PASSWORD_ICON = 'images/icon.png'
FOLDER_ICON = 'images/folder.png'
MORE_ICON = 'images/more.png'
WARNING_ICON = 'images/warning.png'
PASSWORD_DESCRIPTION = 'Enter to copy to the clipboard'
FOLDER_DESCRIPTION = 'Enter to navigate to'

WRONG_PATH_ITEM = ExtensionResultItem(icon=WARNING_ICON,
                                      name='Invalid path',
                                      description='Please check your arguments.',
                                      on_enter=DoNothingAction())

MORE_ELEMENTS_ITEM = ExtensionResultItem(icon=MORE_ICON,
                                         name='Keep typing...',
                                         description='More items are available.'
                                         + ' Narrow your search by entering a pattern.',
                                         on_enter=DoNothingAction())

NO_FILENAME_ITEM = ExtensionResultItem(icon=WARNING_ICON,
                                       name='Please enter a filename',
                                       description='Please check your arguments.',
                                       on_enter=DoNothingAction())


class PassExtension(Extension):
    """ Extension class, does the searching """

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, path=None, pattern=None, depth=None):
        """ Launches a find command with the specified pattern """

        store_location = os_path.expanduser(self.preferences['store-location'])

        if not path:
            path = ''

        if not pattern:
            pattern = ''

        if depth:
            max_depth = '-maxdepth {} '.format(str(depth))
        else:
            max_depth = ''

        searching_path = os_path.join(store_location, path)

        cmd_files = ("find {} {}-type f -not " +
                     "-path *.git* -not -name .* -iname *{}*").format(searching_path,
                                                                      max_depth,
                                                                      pattern)

        cmd_dirs = ("find {} {}-type d -not " +
                    "-path *.git* -not -name .* -iname *{}*").format(searching_path,
                                                                     max_depth,
                                                                     pattern)

        files = re.findall("{}/*(.+).gpg".format(searching_path),
                           check_output(cmd_files.split(" ")))
        dirs = re.findall("{}/*(.+)".format(searching_path),
                          check_output(cmd_dirs.split(" ")))

        files.sort()
        dirs.sort()

        return files, dirs


class KeywordQueryEventListener(EventListener):
    """ KeywordQueryEventListener class used to manage user input"""

    def __init__(self):
        self.extension = None

    def render_results(self, path, files, dirs, keyword):
        """ Prepares the results for the UI """
        items = []
        limit = int(self.extension.preferences['max-results'])

        if limit < len(dirs) + len(files):
            items.append(MORE_ELEMENTS_ITEM)

        for _dir in dirs:
            limit -= 1
            if limit < 0:
                break

            action = SetUserQueryAction("{0} {1}/".format(keyword,
                                                          os_path.join(path, _dir)))
            items.append(ExtensionResultItem(icon=FOLDER_ICON,
                                             name="{0}".format(_dir),
                                             description=FOLDER_DESCRIPTION,
                                             on_enter=action))

        for _file in files:
            limit -= 1
            if limit < 0:
                break

            action = RunScriptAction("pass -c {0}/{1}".format(path, _file), None)
            items.append(ExtensionResultItem(icon=PASSWORD_ICON,
                                             name="{0}".format(_file),
                                             description=PASSWORD_DESCRIPTION,
                                             on_enter=action))

        return items

    def on_event(self, event, extension):
        """ On user input """

        self.extension = extension

        # Get keyword and arguments from event
        query_keyword = event.get_keyword()
        query_args = event.get_argument()

        # Initialize variables
        path = ''
        files = []
        dirs = []
        misc = []
        no_filename = False
        path_not_exists = False

        if not query_args:

            # No arguments specified, list folders and passwords in the password-store root
            files, dirs = self.extension.search(depth=1)
        else:

            # Splitting arguments into path and pattern
            path = os_path.split(query_args)[0]
            pattern = os_path.split(query_args)[1]

            # If the path begins with a slash we remove it
            if path.startswith('/'):
                path = path[1:]

            store_location = os_path.expanduser(self.extension.preferences['store-location'])
            depth = None

            if not os_path.exists(os_path.join(store_location, path)):

                path_not_exists = True
                if query_keyword == extension.preferences['pass-search']:

                    # If specified folder does not exist and we are in searching mode,
                    # show the user an error
                    misc.append(WRONG_PATH_ITEM)

            if not pattern:

                # If the path exists and there is no pattern, only show files
                # and dirs in the current location
                depth = 1

                if query_keyword == extension.preferences['pass-generate']:

                    # If we are in generation mode and no pattern is given,
                    # show the user an error
                    no_filename = True
                    misc.append(NO_FILENAME_ITEM)

            if not no_filename and query_keyword == extension.preferences['pass-generate']:

                # If the user specified a pattern and we are in generation mode
                # give him the possibility to generate the password
                action = RunScriptAction(
                    "pass generate -c {}".format(os_path.join(path, pattern)),
                    None)

                misc.append(ExtensionResultItem(
                    icon=PASSWORD_ICON,
                    name='Generate /{}'.format(os_path.join(path, pattern)),
                    description='Enter to generate and save password',
                    on_enter=action))

            # If the specified path doesn't exist it makes no sense to search for a password
            if not path_not_exists:
                files, dirs = self.extension.search(path=path, pattern=pattern, depth=depth)

        if query_keyword == extension.preferences['pass-generate']:

            # If we are in generation mode we can remove the files
            files = []

        return RenderResultListAction(misc + self.render_results(path, files, dirs, query_keyword))


if __name__ == '__main__':
    PassExtension().run()
