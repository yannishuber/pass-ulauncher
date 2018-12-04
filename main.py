from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from subprocess import check_output, Popen
from os import path
import re


class PassExtension(Extension):

    def __init__(self):
        super(PassExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def search(self, pattern):

        store_location = self.preferences['store-location']

        if "~" in store_location:
            store_location = path.expanduser(store_location)

        cmd = ["find",
               store_location,
               "-iname",
               "*%s*.gpg" % pattern]
        matches = re.findall("%s/*(.+).gpg" % store_location, check_output(cmd))

        return matches

    def copy_to_clipboard(self, item):
        return RunScriptAction("pass -c %s" % item, None)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        query_arg = event.get_argument()

        if not query_arg or len(query_arg) < 3:
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name='Keep typing...',
                on_enter=DoNothingAction())])

        for i in extension.search(query_arg):
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='%s' % i,
                                             description='Enter to copy to the clipboard',
                                             on_enter=extension.copy_to_clipboard(i)))

        return RenderResultListAction(items)


if __name__ == '__main__':
    PassExtension().run()
