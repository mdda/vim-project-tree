import os
import re, configparser

try:
  import vim
  vim_launch_directory=vim.eval('g:vim_launch_directory')
except:
  print("No vim module available outside vim")
  vim_launch_directory=None

config_dir_choices = ['./.editor', './.geany', ]
config_dir_arr=[]

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
  
def _find_config_dir(base):
  for c in config_dir_choices:
    base_config = os.path.join(base, c)
    if os.path.isdir(base_config):
      #print(f"Found directory {base_config}")
      return base_config
  return None
      

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

def _redraw_sidebar():
  sidebar_buffer[:]=None # Empty
  _reset_positions(tree_root)
  _render_in(sidebar_buffer, tree_root)
  #del sidebar_buffer[0]
  sidebar_buffer[0]='[Vim Project Tree]'

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

def _delete_from_tree(arr, position):
  for i, ele in enumerate(arr):
    if ele.position==position:
      del arr[i]
      break
    if 'g'==ele.sidetype and ele.is_open:
      _delete_from_tree(ele.children, position)

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

def _insert_element_at_row(row_line, element_new):
  if row_line is None:  # Add to start of Tree
    tree_root.insert(0, element_new)
  else:
    if 'g'==row_line.sidetype and row_line.is_open:  # insert new child
      row_line.children.insert(0, element_new )
    else: # new entry goes after row_line on same level
      _insert_in_tree(tree_root, row_line.position, element_new)
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
    _insert_element_at_row(row_line, element_new)
    vim.current.window.cursor = row+1, col  # Should be on added line

  elif 'AddFile'==key:
    vim.command(f'wincmd l')  
    name    =vim.eval("expand('%:t')")
    filename=vim.eval("expand('%:.')")
    vim.command(f'wincmd t')  
    log(f"'{name}' -> '{filename}'")
    
    element_new=Sideline('f', name, filename=filename)
    _insert_element_at_row(row_line, element_new)
    vim.current.window.cursor = row+1, col  # Should be on added line

  elif 'Delete'==key:
    if row_line is not None:
      confirm=vim.eval(f"""input('Type YES to delete "{row_line.label}" : ')""")
      log(confirm)
      if 'YES'==confirm: 
        _delete_from_tree(tree_root, row)
        _redraw_sidebar()
        vim.current.window.cursor = row-1, col

  elif 'Rename'==key:
    if row_line is not None:
      name=vim.eval(f"""input('Enter new name for "{row_line.label}" : ')""")
      log(f"New Name='{name}'")
      if 0==len(name): return # Nothing to do
      row_line.label=name
      _redraw_sidebar()
      vim.current.window.cursor = row-1, col
      
  elif 'SaveProject'==key:
    config_dif=_query_for_config_dir()
    if config_dif is None: return 
    _save_project_tree(tree_root, os.path.join(config_dir, config_tree_layout_file))
    
  elif 'SaveSession'==key:
    config_dif=_query_for_config_dir()
    if config_dif is None: return 
    _save_session_files(os.path.join(config_dir, config_session_file))
    
  else:
    log("Unhandled keypress")
    
def _query_for_config_dir():
  if 0==len(config_dir_arr):
    config_dir=vim.eval(f"""input('Path for saving : ', "{os.path.join(vim_launch_directory, config_dir_choices[0])}")""")
    if config_dir is None: return None
    os.makedirs(config_dir, exist_ok=True)
    log(f"config_dir set to ='{config_dir}'")
  else:
    config_dir = config_dir_arr[0]
  return config_dir

def _save_project_tree(tree_root, config_file):
  config = configparser.ConfigParser()

  def _save_project_tree_branch(section, arr):
    config.add_section(section)
    i, finished = 10, False
    for i, ele in enumerate(arr):
      #log(f'* {ele.label:s}:{ele.position}')
      j=(i+1)*10
      
      if 'f'==ele.sidetype:  
        config.set(section, "%d" % (j,), ele.filename)
      else:
        #_log_tree(ele.children)
        config.set(section, "%d-group" % (j,), ele.label)
        _save_project_tree_branch(section+'/'+ele.label, ele.children)

  ## Now walk along the whole 'model', creating groups = sections, and files as we go
  _save_project_tree_branch('.', tree_root)
  
  with open(config_file, 'w') as fout:
    config.write(fout)

def _save_session_files(config_file):
  config = configparser.ConfigParser()
    
  open_files_section = "open-files"
  config.add_section(open_files_section)
  
  vim.command(f'wincmd l')  # Move into the 'main window'
  buf_current = vim.current.buffer

  for b in vim.buffers:
    #log(f"buffer[{b.number}] = {b.name}:{vim.current.window.cursor[0]} {b.options['bufhidden']}+{b.options['buftype']}")
    if b'hide'==b.options['bufhidden'] or b'nofile'==b.options['buftype']:  # NB: 'b' required for byte-strings
      continue
    vim.current.buffer=b
    log(f"buffer[{b.number}] = {b.name}:{vim.current.window.cursor[0]}")

    filename = b.name
    file_relative = os.path.relpath(filename, vim_launch_directory)
    if len(file_relative)<len(filename):
      filename=file_relative

    at_line = vim.current.window.cursor[0]
    config.set(open_files_section, "%d" % (b.number*10,), f"{filename}:{at_line}")

  vim.current.buffer = buf_current
  vim.command(f'wincmd t')  # top-left window

  with open(config_file, 'w') as fout:
    config.write(fout)

    
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
  for key, value in {'<CR>':'Select', 'f':'AddFile', 'g':'AddGroup', 'd':'Delete', 'r':'Rename', 'p':'SaveProject', 's':'SaveSession', 'm':'Move', }.items():
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
    
    config_dir = _find_config_dir(vim_launch_directory)
    log(f"config_dir='{config_dir}'")
    
    session_path = None
    if config_dir is not None:
      session_path = os.path.join(config_dir, config_session_file)
      config_dir_arr.append(config_dir)
    #print(f"session_path = {session_path}")

    if session_path is not None and os.path.isfile( session_path ):
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


    tree_path, tree_root = None, []
    if config_dir is not None:
      tree_path = os.path.join(config_dir, config_tree_layout_file)

    if tree_path is not None and os.path.isfile( tree_path ):
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
            filename = vd['']
            arr.append( Sideline('f', os.path.basename(filename), filename=filename) )
              
          else:  # This is something special
            if 'group' in vd:
              group = vd['group']
              ## Add the group to the tree, and recursively go after that section...
              arr.append( Sideline('g', group, is_open=False) )
              ### Descend with parent=current
              _load_project_tree_branch(section+'/'+group, arr[-1].children )  # Add to group's children array

      if config.has_section('.'):
        _load_project_tree_branch('.', tree_root)
        #print(tree)
    
    _redraw_sidebar()
