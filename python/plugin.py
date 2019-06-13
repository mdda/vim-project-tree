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

class Sideline:
  def __init__(self, sidetype, label, filename=None, is_open=False):
    self.sidetype=sidetype
    self.label=label
    self.position=None
    if 'f'==self.sidetype:
      self.filename=filename
    else:
      self.children=[]
      self.is_open=is_open

if vim_launch_directory is not None:
  # Code to initialise plugin view here
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

  vim.command(f'setlocal cursorline')  # underlines current cursor line (looks Ok)

  vim.command(f'nnoremap <buffer> <CR> :SidebarEnter<CR>')



  #vim.command(f'iabc <buffer>')  # ???

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
            arr.append( Sideline('f', vd[''], filename=vd['']) )
              
          else:  # This is something special
            if 'group' in vd:
              group = vd['group']
              ## Add the group to the tree, and recursively go after that section...
              arr.append( Sideline('g', group, is_open=False) )
              ### Descend with parent=iter
              _load_project_tree_branch(section+'/'+group, arr[-1].children )  # Add to group's children array

      def _reset_positions(arr):
        for ele in arr:
          ele.position=None
          if 'g'==ele.sidetype: 
            _reset_positions(ele.children)
          
      def _render_in_sidebar(arr, indent=0):
        for ele in arr:
          ele.position=len(sidebar_buffer)+1 # For vim line numbering
          if 'f'==ele.sidetype: # Filenode
            sidebar_buffer.append(' '*indent + '  ' +ele.label + str(ele.position))
          elif 'g'==ele.sidetype: # Group
            if ele.is_open:
              sidebar_buffer.append(' '*indent + 'v ' +ele.label )
              _render_in_sidebar(ele.children, indent=indent+2)
            else:
              sidebar_buffer.append(' '*indent + '> ' +ele.label )
      
      tree_root = []
      if config.has_section('.'):
        _load_project_tree_branch('.', tree_root)
        #print(tree)
        
      sidebar_buffer[:]=None # Empty
      _reset_positions(tree_root)
      _render_in_sidebar(tree_root)
      
      #del sidebar_buffer[0]
      sidebar_buffer[0]='[Save Project]'

def sidebar_enter():
  sidebar_buffer.append("ENTER")
  
