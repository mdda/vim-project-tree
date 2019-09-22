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
log_height, log_buffer =  10,None

#def insert_country():
#  row, col = vim.current.window.cursor
#  current_line = vim.current.buffer[row-1]
#  new_line = current_line[:col] + _get_country() + current_line[col:]
#  vim.current.buffer[row-1] = new_line

def log(txt, clear=False):
  if log_buffer is None: return
  if clear: log_buffer[:]=None
  log_buffer.append(txt)
  
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

  # Global set of 'hidden' : https://medium.com/usevim/vim-101-set-hidden-f78800142855
  vim.command(f'set hidden')  

  if log_height>0:
    vim.command(f'belowright {log_height:d} new') 
    log_buffer=vim.buffers[len(vim.buffers)]  # 'sidebar' is the last opened buffer
    log_buffer.name='plugin.log'
    log_buffer.options['bufhidden']='hide' # no need to list this file in buffers
    log_buffer.options['buftype']='nofile' # no need to write this file on exit
    
  vim.command(f'topleft vertical {sidebar_width:d} new') 

  #vim.command(f'nnoremap <buffer> <CR> :SidebarEnter<CR>')  # Calls via command! -> function! -> python
  #https://github.com/scrooloose/nerdtree/blob/master/lib/nerdtree/key_map.vim#L58
  # <silent> 
  #vim.command(f'nnoremap <buffer> <CR> :python3 plugin.sidebar_enter()<CR>')  # Calls into python directly
  for key, value in {'<CR>':'Select', 'f':'AddFile', 'g':'AddGroup', 'd':'Delete', 'm':'Move', 'r':'Rename', 'p':'SaveProject', 's':'SaveSession', }.items():
    vim.command(f'nnoremap <buffer> <silent> {key} :python3 plugin.sidebar_key("{value}")<CR>')  # Calls into python directly

  sidebar_buffer = vim.buffers[len(vim.buffers)]  # 'sidebar' is the last opened buffer
  sidebar_buffer.name='sidebar'

  # https://github.com/scrooloose/nerdtree/blob/master/lib/nerdtree/creator.vim#L288
  #" Options for a non-file/control buffer.
  
  # https://vimhelp.org/options.txt.html#global-local
  #vim.command(f'setlocal bufhidden=hide')
  #vim.command(f'setlocal buftype=nofile')
  sidebar_buffer.options['bufhidden']='hide' # no need to list this file in buffers
  sidebar_buffer.options['buftype']='nofile' # no need to write this file on exit
  
  sidebar_buffer.options['modifiable']='off' # no changes allowed (??works??)
  #vim.command(f'setlocal modifiable')  
  #vim.command(f'setlocal nomodifiable')  # Actually works (a little too well)  
  
  vim.command(f'setlocal noswapfile')

  #" Options for controlling buffer/window appearance.
  vim.command(f'setlocal foldcolumn=0')
  vim.command(f'setlocal foldmethod=manual')
  vim.command(f'setlocal nobuflisted')
  vim.command(f'setlocal nofoldenable')
  vim.command(f'setlocal nolist')
  
  vim.command(f'setlocal nospell')
  
  vim.command(f'setlocal nowrap')
  #sidebar_buffer.options['wrap']='off' # RHS falls off (no wrapping of text)  FAIL
  
  vim.command(f'setlocal nu')  # Linenumbers
  #vim.command(f'setlocal rnu')  # Relative linenumbers

  vim.command(f'setlocal cursorline')  # underlines current cursor line (looks Ok)

  #vim.command(f'iabc <buffer>')  # ???

  
  #vim.command(f'file {sidebar_buffer:s}') 
  #vim.command(f'edit {sidebar_buffer:s}') 
  #vim.command(f'vertical resize {sidebar_width:d}') 

  #sidebar_buffer[:] = None  # Remove all content
  #sidebar_buffer[0] = '--line 0--'
  #sidebar_buffer.append(["Hello", "World"]) # Adds to bottom (blank line at top)
  #sidebar_buffer[:] = ["Hello", "World"]  # Works


  if os.path.isdir(vim_launch_directory):
    #log("Found launch directory")
    session_path = os.path.join(vim_launch_directory, '.geany', config_session_file)
    #if False:
    if os.path.isfile( session_path ):
      vim.command(f'wincmd l')  
      
      with open(session_path, 'r') as fin:
        # https://docs.python.org/3/library/configparser.html
        config = configparser.ConfigParser()
        config.readfp(fin)
        
      #print("Sections", config.sections())
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
            log(f"LOADING : file_relative:line = {file_relative:s}:{at_line:d}")
            vim.command(f'silent edit {file_relative:s}') 
            vim.current.window.cursor = at_line,0
            
      vim.command(f'wincmd t')  # top-left window

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
          
      def _scan_tree(arr, position):
        found=None
        for ele in arr:
          if ele.position==position:
            found=ele
            break
          if 'g'==ele.sidetype and ele.is_open:
            below=_scan_tree(ele.children, position)
            if below is not None:
              found=below
              break
        return found

      def _insert_in_tree(arr, position, element_new):
        for i, ele in enumerate(arr):
          if ele.position==position:
            arr.insert(i+1, element_new)
          if 'g'==ele.sidetype and ele.is_open:
            _insert_in_tree(ele.children, position, element_new)            

      def _log_tree(arr):
        for ele in arr:
          log(f'* {ele.label:s}:{ele.position}')
          if 'g'==ele.sidetype:  # Ignore is_open
            _log_tree(ele.children)
          
      def _render_in(buf, arr, indent=0):
        for ele in arr:
          ele.position=len(buf)+1 # For vim line numbering
          if 'f'==ele.sidetype: # Filenode
            buf.append(' '*indent + '  ' +ele.label)  #  + str(ele.position)
          elif 'g'==ele.sidetype: # Group
            if ele.is_open:
              buf.append(' '*indent + 'v ' +ele.label )
              _render_in(buf, ele.children, indent=indent+2)
            else:
              buf.append(' '*indent + '> ' +ele.label )
      
      tree_root = []
      if config.has_section('.'):
        _load_project_tree_branch('.', tree_root)
        #print(tree)
      
      def _redraw_sidebar():
        sidebar_buffer[:]=None # Empty
        _reset_positions(tree_root)
        _render_in(sidebar_buffer, tree_root)
        #del sidebar_buffer[0]
        sidebar_buffer[0]='[Vim Project Tree]'
        
      _redraw_sidebar()
      

#def sidebar_enter():
#  sidebar_buffer.append("ENTER")
  
def sidebar_key(key):
  row, col = vim.current.window.cursor
  log(f"KeyPress = '{key}' at {row}", clear=True)
  row_line = _scan_tree(tree_root, row)  # Almost always used
  
  if 'Select'==key:
    #_log_tree(tree_root)
    #log(f"RowFound = '{row_line}'")
    
    if row_line is not None:
      #log(f"line = '{row_line.label}'")
      if 'g'==row_line.sidetype:
        row_line.is_open = not row_line.is_open  # Invert
        _redraw_sidebar()
        vim.current.window.cursor = row, col
      else:
        filename=row_line.filename
        #log(f" -> {filename:s}")
        vim.command(f'wincmd l')  
        vim.command(f'edit {filename:s}') 
        
  elif 'AddGroup'==key:
    #vim.command("call inputsave()")
    name=vim.eval("input('Enter name for new Group : ')")
    #vim.command("call inputrestore()")
    
    log(f"New Group Name='{name}'")
    if 0==len(name): return # Nothing to do

    element_new=Sideline('g', name, is_open=False)
    #_insert_element_at_row(tree_root, row_line, element_new)
    
    if row_line is None:  # Add to start of Tree
      tree_root.insert(0, element_new)
    else:
      if 'g'==row_line.sidetype and row_line.is_open:  # insert new child
        row_line.children.insert(0, element_new )
      else: # new entry goes after row_line on same level
        _insert_in_tree(tree_root, row, element_new)
    _redraw_sidebar()
    vim.current.window.cursor = row+1, col  # Should be on added line

  elif 'AddFile'==key:
    name='sdfsdf'
    filename='sdfsdf/sdfsdf'
    element_new=Sideline('f', name, filename=filename)
    
  else:
    log("Unhandled keypress")