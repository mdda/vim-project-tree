## vim project tree (Python plugin)

The skeleton of this project was taken from [this template repo](https://github.com/mdda/vim-plugin-python).

Key references are going to be :
*  https://github.com/scrooloose/nerdtree/tree/master/lib/nerdtree
*  https://www.tummy.com/presentations/vimpython-20070225/
*  https://vimhelp.org/if_pyth.txt.html
*  https://devhints.io/vimscript



## Motivation 

This plugin creates a vim sidebar with a 'project-tree' view of your files.  

The project-tree view can be different from how they're laid out on disk : 
Personally, I prefer to keep a 'thematic' structure to a project - 
at the very least, it can be handy to keep files in an order not dictated by their sequence alphabetically.

<!-- ![Screenshot](./img/vim-project-tree_screenshot-1.png?raw=true)  !-->

The plugin is also designed to keep separate state for different repository folders, with the state being stored locally, 
so that one can put it into version control, for instance.

I had previously contributed to a separate sidebar widget/app for SciTE, called SciTEpm (which is why this plugin
contains a loader for the xml files that SciTEpm saves).  
And then made a much nicer one for `geany`.  However, `geany` decided to completely revamp their plugin system 
when moving from `gtk2` to `gtk3` and the python connectors abruptly stopped working for me.  
Hence the move.


## File Layout

For each actual project that you have (as distinct from what Geany calls projects), typically one would 
launch Geany from its root directory (where the .git directory is stored, for instance).

The project-tree plugin's files are stored in a '.editor' directory (it will confirm before writing anything to disk) :

 * .editor
   + project-tree-layout.ini
   + session.ini
   + session_default.ini # TODO, maybe
 * ... the rest of your files ...

For backwards compatibility, it will also search in `.geany` and use that as 
its storage directory if they are found there initially.

Of these files:
 * 'project-tree-layout.ini' will be relatively static (once the project is in mainenance mode), 
    so could well be *put under version control*
 * 'session.ini' is just a listing of open files (with line numbers, and TODO read-only status), 
    so is probably *not sensible to put under version control*
 * 'session_default.ini' (TODO) is only read if session.ini doesn't exist - 
    so could be used as a starter set of relevant files for newcomers,
    and could well be *put under version control* if you want to have one (not necessary)
 
 
##  Installation

With Vim 8.0 and after, there's a built-in package manager.  So you can create the necessary directory within the autoload hierarchy 
(here `mdda` is just an arbitrary choice), and then clone this repo into there directly.  (Alternatively, you can create symlink from there too) :

```
pushd . 
mkdir -p ~/.vim/pack/mdda/start
cd  ~/.vim/pack/mdda/start
git clone https://github.com/mdda/vim-project-tree.git
# OR : ln -s ~/your-src-directory/vim-project-tree .
popd
```


## Usage 

The project-tree sidebar has keys assigned, their operation refers to the current cursor line within the sidebar :
 * 'Enter' - open file, or open/close group based on the current line
 * 'f' - Add the currently open document filename below the current line
 * 'g' - Add a new group heading below the current line (prompts for name)
 * 'd' - Delete current entry (after confirmation prompt)
 * 'r' - Rename current entry (prompts for name)
 * TODO : 'm' - Move current entry to after the line given in response to a prompt
 * 'p' - Save project-tree
 * 's' - Save current session, with line numbers (TODO : and read-only flag)
 
TODO : When loaded for the first time in a directory, it's immediately ready to use : If you decided to save 
the tree or the session it will ask whether to create the '.editor' folder.



## Commentary

### INI files

The .ini files are standard form, while enabling the storing of the full tree structure.

