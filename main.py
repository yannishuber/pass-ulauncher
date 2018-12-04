from distutils import dep_util
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from subprocess import check_output
from os import path
import re


class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, path_ext='', pattern='', depth=None):

        store_location = path.expanduser(self.preferences['store-location'])

        if store_location.endswith('/'):
            store_location = store_location[:-1]

        searching_path = "{0}/{1}".format(store_location, path_ext)

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
            if '/' in query_arg:
                params = re.match("(.*)/(\w+)?", query_arg)
                path_ext = params.group(1)
                pattern = "" if not params.group(2) else params.group(2)
                result = extension.search(path_ext=path_ext, pattern=pattern, depth=1)
            else:
                result = extension.search(pattern=query_arg)

        for i in result[:6]:

            if ".gpg" in i:
                # is a password

                # remove extension
                i = i[:-4]

                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name="{0}".format(i),
                                                 description='Enter to copy to the clipboard',
                                                 on_enter=RunScriptAction(
                                                     "pass -c {0}/{1}".format(path_ext, i), None)))
            else:
                # is a directory
                items.append(ExtensionResultItem(icon='images/folder.png',
                                                 name="{0}".format(i),
                                                 description='Enter to navigate',
                                                 on_enter=SetUserQueryAction(
                                                     "{0} {1}/{2}/".format(extension.preferences['pass_kw'], path_ext, i))))

        return RenderResultListAction(items)


if __name__ == '__main__':
    PassExtension().run()
