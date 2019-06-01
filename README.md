## vim project tree (Python plugin)

The skeleton of this project was taken from [this template repo](https://github.com/mdda/vim-plugin-python).

Key references are going to be :
*  https://github.com/scrooloose/nerdtree/tree/master/lib/nerdtree
*  https://www.tummy.com/presentations/vimpython-20070225/



## Motivation 

This plugin creates a vim sidebar with a 'project-tree' view of your files.  

The project-tree view can be different from how they're laid out on disk : 
Personally, I prefer to keep a 'thematic' structure to a project - 
at the very least, it can be handy to keep files in an order not dictated by their sequence alphabetically.

<!-- ![Screenshot](./img/geany-project-tree_screenshot-1.png?raw=true)  !-->

The plugin is also designed to keep separate state for different repository folders, with the state being stored locally, 
so that one can put it into version control, for instance.

I had previously contributed to a separate sidebar widget/app for SciTE, called SciTEpm (which is why this plugin
contains a loader for the xml files that SciTEpm saves).  And then made a much nicer one for `geany`.  However,
`geany` decided to completely revamp their plugin system when moving from `gtk2` to `gtk3` and the 
python connectors abruptly stopped working for me.  Hence the move.


## File Layout

For each actual project that you have (as distinct from what Geany calls projects), typically one would 
launch Geany from its root directory (where the .git directory is stored, for instance).

The project-tree plugin's files are stored in a '.geany' directory (it will confirm before writing anything to disk) :

 * .geany
   + project-tree-layout.ini
   + session.ini
   + [OPTIONAL: project-tree-layout_devel.ini]
   + [OPTIONAL: session_default.ini ] 
 * ... the rest of your files ...

Of these files:
 * 'project-tree-layout.ini' will be relatively static (once the project is in mainenance mode), so could well be put into version control
 * 'session.ini' is just a dump of open files, so is probably not sensible to put into version control
 * 'project-tree-layout_devel.ini' is read-only, for testing
 * 'session_default.ini' is used if session.ini doesn't exist - so could be used as a starter set of relevant files for newcomers
 
 
## Usage 

*All TODO for the vim version*

The project-tree sidebar can be right-clicked, to get to :
 * 'Add this file', which adds the currently open document to the project-tree
 * 'Add group', which adds a new group heading
 * and other functions that should be obvious
 
It also allows drag-and-drop internally, so you can organize files & groups to your heart's content.

At the top of the sidebar is a quick menu, allowing you to Load/Save the Project-Tree layout, and current open files.

When loaded for the first time in a directory, it's immediately ready to use : It will ask whether to create the 
'.geany' folder if you need to save the tree or the session.


## Commentary

### INI files

The .ini files are standard form, while enabling the storing of the full tree structure.
