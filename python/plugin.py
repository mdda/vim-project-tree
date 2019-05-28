import json

try:
  import vim
except:
  print("No vim module available outside vim")
  pass

def insert_country():
  row, col = vim.current.window.cursor
  current_line = vim.current.buffer[row-1]
  new_line = current_line[:col] + _get_country() + current_line[col:]
  vim.current.buffer[row-1] = new_line
