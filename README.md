# Ulauncher password-store extension

[![Build Status](https://travis-ci.com/yannishuber/pass-ulauncher.svg?branch=master)](https://travis-ci.com/yannishuber/pass-ulauncher)

> A simple [pass](https://www.passwordstore.org/) extension for [Ulauncher](https://ulauncher.io/).

![Demo](demo.gif)

## Usage
### Search
To search your password store : `ps <input>` will return every password or folder that matches your given `input`.
### Generation
You can directly generate a new password by typing : `pg <path>/<input>`. 
This will generate a new password in a file `input` in the optional given 
`path`.


## Installation
To install the extension go to the Ulauncher preferences -> extensions -> add extension and paste : `https://github.com/yannishuber/pass-ulauncher`

## Development

    $ git clone https://github.com/yannishuber/pass-ulauncher.git
    $ ln -s pass-ulauncher/ ~/.cache/ulauncher_cache/extensions/pass-ulauncher/
 
 In order to see the new extension you have to restart Ulauncher.
 
## TODO
- [x] Information if not all elements are listed
- [x] List directories first
- [ ] Check user preferences
- [x] Possibility to add a new password
- [ ] Git controls (push/pull password-store repo)

## Credits
Icons made by [Freepik](https://www.freepik.com/) and [Smashicons](https://www.flaticon.com/authors/smashicons) from [Flaticon](https://www.flaticon.com/).