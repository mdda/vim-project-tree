import json

try:
  import vim
  vim_launch_directory=vim.eval('g:vim_launch_directory')
except:
  print("No vim module available outside vim")
  vim_launch_directory=None

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
  sidebar_buffer[:] = ["Hello", "World"]
  
  