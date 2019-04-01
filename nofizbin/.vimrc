" comments start with these quotes for some reason
syn on	" turn on syntax highlighting
set tabstop=4	" set tab width
set nu	" show line numbers to left of text
set ruler	" show row, col in lower-right corner
set ignorecase	" case-insensitive search (/ and ?)
"set spell	" use spell-checking
"set spellfile=c:\\mza\\build\\bin\\nofizbin\\vimspell.add
set spellfile=~/build/bin/nofizbin/vimspell.add
set nocompatible	" vim-specific mode
set backspace=2	" set backspace key to work like most other editors
set scrolloff=5	" keep at least 5 lines above/below
"set nohls	" don't highlight the search
set hlsearch	" highlight the search
set dir=~/tmp
set nobk	" do not make backups when overwriting files
set guifont=Monospace 10:h10:cANSI:qDRAFT
set formatoptions-=cro " don't automatically continue comments
" for win32, make a file c:\\Users\\blah\\_vimrc and have it contain the (uncommented) line:
" source c:\\\\blah\\build\\bin\\nofizbin\\.vimrc

autocmd BufReadPost *
	\ if line("'\"") > 1 && line("'\"") <= line("$") |
	\   exe "normal! g`\"" |
	\ endif

" vim: set ts=17:

