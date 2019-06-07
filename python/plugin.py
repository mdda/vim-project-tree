import os
import re, configparser

try:
  import vim
  vim_launch_directory=vim.eval('g:vim_launch_directory')
except:
  print("No vim module available outside vim")
  vim_launch_directory=None

config_tree_layout_file           = "project-tree-layout.ini"
config_session_file               = "session.ini"

def insert_country():
  row, col = vim.current.window.cursor
  current_line = vim.current.buffer[row-1]
  new_line = current_line[:col] + _get_country() + current_line[col:]
  vim.current.buffer[row-1] = new_line

sidebar_width=30

if vim_launch_directory is not None:
  pass
  # Stuff to initialise plugin view here
  # https://github.com/scrooloose/nerdtree/blob/master/lib/nerdtree/creator.vim#L187
  vim.command(f'topleft vertical {sidebar_width:d} new') 
  vim.command(f'setlocal nowrap')
  sidebar_buffer = vim.buffers[len(vim.buffers)]
  sidebar_buffer.name='sidebar'
  
  # https://vimhelp.org/options.txt.html#global-local
  sidebar_buffer.options['buftype']='nofile' # no need to write this file on exit
  
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
    if os.path.isfile( session_path ):
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
