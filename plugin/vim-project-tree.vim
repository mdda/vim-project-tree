if !has("python3")
  echo "vim has to be compiled with +python3 to run this"
  finish
endif

if exists('g:python_project_tree_plugin_loaded')
  finish
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
let g:vim_launch_directory = getcwd()

python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import plugin
#print("vim_launch_directory", plugin.vim_launch_directory)  #WORKS
EOF

"function! SidebarEnter()
"  python3 plugin.sidebar_enter()
"endfunction
"command! -nargs=0 SidebarEnter call SidebarEnter()

let g:python_project_tree_plugin_loaded = 1

