from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from subprocess import check_output
from os import path as os_path
import re

PASSWORD_ICON = 'images/icon.png'
FOLDER_ICON = 'images/folder.png'
MORE_ICON = 'images/more.png'
WARNING_ICON = 'images/warning.png'
PASSWORD_DESCRIPTION = 'Enter to copy to the clipboard'
FOLDER_DESCRIPTION = 'Enter to navigate to'

WRONG_PATH_ITEM = ExtensionResultItem(icon=WARNING_ICON,
                                      name='Invalid path',
                                      description='Please check your arguments.',
                                      on_enter=DoNothingAction()
                                      )
MORE_ELEMENTS_ITEM = ExtensionResultItem(icon=MORE_ICON,
                                         name='Keep typing...',
                                         description='More items are available.'
                                                     + ' Narrow your search by entering a pattern.',
                                         on_enter=DoNothingAction())


class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, path=None, pattern=None, depth=None):

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

        cmd_files = "find {} {}-type f -not -path *.git* -not -name .* -iname *{}*".format(searching_path,
                                                                                           max_depth,
                                                                                           pattern)

        cmd_dirs = "find {} {}-type d -not -path *.git* -not -name .* -iname *{}*".format(searching_path,
                                                                                          max_depth,
                                                                                          pattern)

        files = re.findall("{}/*(.+).gpg".format(searching_path), check_output(cmd_files.split(" ")))
        dirs = re.findall("{}/*(.+)".format(searching_path), check_output(cmd_dirs.split(" ")))

        files.sort()
        dirs.sort()

        return files, dirs


class KeywordQueryEventListener(EventListener):

    def __init__(self):
        self.extension = None

    def search_event(self, arguments):
        path = ''
        if not arguments:

            # No arguments specified, list folders and passwords in the password-store root
            files, dirs = self.extension.search(depth=1)
        else:

            # Splitting arguments into path and pattern
            path = os_path.split(arguments)[0]
            pattern = os_path.split(arguments)[1]

            # If the path begins with a slash we remove it
            if path.startswith('/'):
                path = path[1:]

            store_location = os_path.expanduser(self.extension.preferences['store-location'])
            depth = None

            if not os_path.exists(os_path.join(store_location, path)):

                # If specified folder does not exist show the user an error
                return RenderResultListAction([WRONG_PATH_ITEM])
            elif not pattern:

                # If the path exists and there is no pattern, only show files
                # and dirs in the current location
                depth = 1

            files, dirs = self.extension.search(path=path, pattern=pattern, depth=depth)

        return RenderResultListAction(self.render_results(path, files, dirs))

    def render_results(self, path, files, dirs):
        items = []
        limit = int(self.extension.preferences['max-results'])

        if limit < len(dirs) + len(files):
            items.append(MORE_ELEMENTS_ITEM)

        for d in dirs:
            limit -= 1
            if limit < 0:
                break

            action = SetUserQueryAction("{0} {1}/".format(self.extension.preferences['pass-search'],
                                                          os_path.join(path, d)))
            items.append(ExtensionResultItem(icon=FOLDER_ICON,
                                             name="{0}".format(d),
                                             description=FOLDER_DESCRIPTION,
                                             on_enter=action))

        for f in files:
            limit -= 1
            if limit < 0:
                break

            action = RunScriptAction("pass -c {0}/{1}".format(path, f), None)
            items.append(ExtensionResultItem(icon=PASSWORD_ICON,
                                             name="{0}".format(f),
                                             description=PASSWORD_DESCRIPTION,
                                             on_enter=action))

        return items

    def on_event(self, event, extension):
        self.extension = extension

        # Get keyword and arguments from event
        query_keyword = event.get_keyword()
        query_args = event.get_argument()

        if query_keyword == extension.preferences['pass-generate']:
            '''
            Password generation
            '''
            # TODO : PASSWORD GENERATION
            pass
        elif query_keyword == extension.preferences['pass-search']:
            '''
            Password searching
            '''
            return self.search_event(query_args)


if __name__ == '__main__':
    PassExtension().run()
