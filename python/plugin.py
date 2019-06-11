import os
import re, configparser

try:
  import vim
  vim_launch_directory=vim.eval('g:vim_launch_directory')
except:
  print("No vim module available outside vim")
  vim_launch_directory=None

config_tree_layout_file = "project-tree-layout.ini"
config_session_file     = "session.ini"

sidebar_width=30

#def insert_country():
#  row, col = vim.current.window.cursor
#  current_line = vim.current.buffer[row-1]
#  new_line = current_line[:col] + _get_country() + current_line[col:]
#  vim.current.buffer[row-1] = new_line

if vim_launch_directory is not None:
  pass
  # Stuff to initialise plugin view here
  # https://github.com/scrooloose/nerdtree/blob/master/lib/nerdtree/creator.vim#L187
  vim.command(f'topleft vertical {sidebar_width:d} new') 

  # https://github.com/scrooloose/nerdtree/blob/master/lib/nerdtree/creator.vim#L288
  #" Options for a non-file/control buffer.
  vim.command(f'setlocal bufhidden=hide')
  vim.command(f'setlocal buftype=nofile')
  vim.command(f'setlocal noswapfile')

  #" Options for controlling buffer/window appearance.
  vim.command(f'setlocal foldcolumn=0')
  vim.command(f'setlocal foldmethod=manual')
  vim.command(f'setlocal nobuflisted')
  vim.command(f'setlocal nofoldenable')
  vim.command(f'setlocal nolist')
  vim.command(f'setlocal nospell')
  vim.command(f'setlocal nowrap')
  
  vim.command(f'setlocal nu')  # Linenumbers
  #vim.command(f'setlocal rnu')  # Relative linenumbers
  
  sidebar_buffer = vim.buffers[len(vim.buffers)]  # 'sidebar' is the last opened buffer
  sidebar_buffer.name='sidebar'
  
  # https://vimhelp.org/options.txt.html#global-local
  #sidebar_buffer.options['buftype']='nofile' # no need to write this file on exit
  
  #vim.command(f'file {sidebar_buffer:s}') 
  #vim.command(f'edit {sidebar_buffer:s}') 
  #vim.command(f'vertical resize {sidebar_width:d}') 

  #sidebar_buffer[:] = None  # Remove all content
  #sidebar_buffer[0] = '--line 0--'
  #sidebar_buffer.append(["Hello", "World"]) # Adds to bottom (blank line at top)
  #sidebar_buffer[:] = ["Hello", "World"]  # Works

  
  if os.path.isdir(vim_launch_directory):
    #sidebar_buffer[:] = ["Found directory"]

    session_path = os.path.join(vim_launch_directory, '.geany', config_session_file)
    if False and os.path.isfile( session_path ):
      # https://docs.python.org/3/library/configparser.html
      with open(session_path, 'r') as fin:
        config = configparser.ConfigParser()
        config.readfp(fin)
        
      print("Sections", config.sections())
      open_files_section = "open-files"
      if config.has_section(open_files_section):
        key_matcher = re.compile("(\d+)-?(\S*)")
        d=dict()
        for k,v in config.items(open_files_section):  ## Need to sort these numerically
          #print("('%s', '%s')" % (k, v))
          m = key_matcher.match(k)
          if m:
            order = int(m.group(1))
            if order not in d: d[order]=dict()
            d[order][m.group(2)] = v
        line_matcher = re.compile("(.*?)\:([\d\.]+)$")
        for k,vd in sorted(d.items()):  # Here, vd is dictionary of data about each 'k' item
          if '' in vd: # This is a file (the default type of item)
            file_relative = vd['']
            m, at_line = line_matcher.match(file_relative), 1
            if m:  # This only matches if there's a line number there
              file_relative = m.group(1)
              at_line = int(m.group(2))
            print("LOADING : file_relative:line = %s:%d" % (file_relative, at_line,))
            #filepath = os.path.join(self.config_base_directory, file_relative)
            #doc = geany.document.open_file(filepath)
            #doc.editor.goto_pos(at_line)
            sidebar_buffer.append( file_relative )
            #vim.command(f':edit {file_relative:s}') 

    tree_path = os.path.join(vim_launch_directory, '.geany', config_tree_layout_file)
    if os.path.isfile( tree_path ):
      with open(tree_path, 'r') as fin:
        config = configparser.ConfigParser()
        config.readfp(fin)
      
      # (type, label, arr/filename)
      # ('g', label, arr)  # g=closed, G=open
      # ('f', label, filename)
      tree=[ ('G', '-', []) ]
      def _load_project_tree_branch(section, arr):
        ## Create a nice dictionary of stuff from this section - each integer(sorted) can contain several entries
        key_matcher = re.compile("(\d+)-?(\S*)")
        d=dict()
        for k,v in config.items(section):
          #print("('%s', '%s')" % (k, v))
          m = key_matcher.match(k)
          if m:
            order = int(m.group(1))
            if order not in d:d[order]=dict()
            d[order][m.group(2)] = v
            
        for k,vd in sorted(d.items()):  # Here, vd is dictionary of data about each 'k' item
          if '' in vd: # This is a file (the default ending)
            ## Just add the file to the tree where we are
            #iter = model.append(parent, TreeViewRowFile(vd[''], label=vd.get('label', None)).row)
            arr.append( ('f', vd[''], None ) ) 
            # No need to store this 'iter' - can easily append after
              
          else:  # This is something special
            if 'group' in vd:
              group = vd['group']
              ## Add the group to the tree, and recursively go after that section...
              #iter = model.append(parent, TreeViewRowGroup(group, label=vd.get('label', None)).row)
              arr.append( ('g', group, [] ) )
              ### Descend with parent=iter
              _load_project_tree_branch(section+'/'+group, arr[-1][2] )  # Add to group's array
      
      def _render_in_sidebar(arr, indent=0):
        for ele in arr:
          if 'f'==ele[0]: # Filenode
            sidebar_buffer.append(' '*indent + '  ' +ele[1] )
          elif 'g'==ele[0]: # closed group
            sidebar_buffer.append(' '*indent + '> ' +ele[1] )
          elif 'G'==ele[0]: # open group
            sidebar_buffer.append(' '*indent + 'v ' +ele[1] )
            _render_in_sidebar(ele[2], indent=indent+2)
      
      if config.has_section('.'):
        #print("Found Root!")
        #model.clear()
        _load_project_tree_branch('.', tree[-1][2])
        #print(tree)
        sidebar_buffer[:]=None # Empty
        _render_in_sidebar(tree[0][2])
        #del sidebar_buffer[0]
        sidebar_buffer[0]='[Save Project]'

