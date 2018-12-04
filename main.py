from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from subprocess import check_output
from os import path
import re

PASSWORD_ICON = 'images/icon.png'
FOLDER_ICON = 'images/folder.png'
PASSWORD_DESCRIPTION = 'Enter to copy to the clipboard'
FOLDER_DESCRIPTION = 'Enter to navigate to'


class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, path_ext='', pattern='', depth=None):

        store_location = path.expanduser(self.preferences['store-location'])

        searching_path = path.join(store_location, path_ext)

        cmd = ['find', searching_path]

        if depth:
            cmd.extend(['-maxdepth', str(depth)])

        cmd.extend(['-not', '-path', '*.git*',
                    '-not', '-name', '.*',
                    '-iname', "*{0}*".format(pattern)])

        matches = re.findall("{0}/*(.+)".format(searching_path), check_output(cmd))

        return matches


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        path_ext = ""

        query_arg = event.get_argument()

        if not query_arg:
            result = extension.search(depth=1)
        else:
            path_ext = path.split(query_arg)[0]
            pattern = path.split(query_arg)[1]

            if path_ext.startswith('/'):
                path_ext = path_ext[1:]

            if not query_arg.endswith('/'):
                result = extension.search(path_ext=path_ext, pattern=pattern)
            else:
                store_location = path.expanduser(extension.preferences['store-location'])

                if not path.exists(path.join(store_location, path_ext)):
                    return RenderResultListAction([ExtensionResultItem(icon=PASSWORD_ICON,
                                                                       name='Invalid path !',
                                                                       description='Please check your arguments.',
                                                                       on_enter=DoNothingAction()
                                                                       )])
                else:
                    result = extension.search(path_ext=path_ext, pattern=pattern, depth=1)

        nb_results = int(extension.preferences["max-results"])

        for i in result[:nb_results]:

            if ".gpg" in i:
                # remove file extension
                i = i[:-4]

                icon = PASSWORD_ICON
                description = PASSWORD_DESCRIPTION
                action = RunScriptAction("pass -c {0}/{1}".format(path_ext, i), None)
            else:
                icon = FOLDER_ICON
                description = FOLDER_DESCRIPTION
                action = SetUserQueryAction("{0} {1}/".format(extension.preferences['pass-keyword'],
                                                              path.join(path_ext, i)))

            items.append(ExtensionResultItem(icon=icon,
                                             name="{0}".format(i),
                                             description=description,
                                             on_enter=action))

        return RenderResultListAction(items)


if __name__ == '__main__':
    PassExtension().run()
