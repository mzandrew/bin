" comments start with these quotes for some reason
" to reload this, do one of these:
" 	:so %
" 	:so $MYVIMRC
" 	:so ~/.vimrc
syn on	" turn on syntax highlighting
set tabstop=4	" set tab width
set nu	" show line numbers to left of text
set ruler	" show row, col in lower-right corner
set ignorecase	" case-insensitive search (/ and ?)
"set spell	" use spell-checking
"set spellfile=c:\\blah\\build\\bin\\nofizbin\\vimspell.add
set spellfile=~/build/bin/nofizbin/vimspell.add
set nocompatible	" vim-specific mode
set backspace=2	" set backspace key to work like most other editors
set scrolloff=5	" keep at least 5 lines above/below
"set nohls	" don't highlight the search
set hlsearch	" highlight the search
set dir=~/tmp
set nobk	" do not make backups when overwriting files
"set guifont=Monospace\ 14	" set guifont? to query
set guifont=Courier_New:h14	" set guifont? to query
set formatoptions-=cro " don't automatically continue comments
" for win32, make a file c:\\Users\\blah\\_vimrc and have it contain the (uncommented) line:
" source c:\\\\blah\\build\\bin\\nofizbin\\.vimrc
set clipboard=exclude:.*

autocmd BufNewFile,BufRead *.v,*.sv set syntax=verilog
autocmd BufReadPost *
	\ if line("'\"") > 1 && line("'\"") <= line("$") |
	\   exe "normal! g`\"" |
	\ endif

" the following are from https://github.com/waveform80/dotfiles/blob/master/vimrc
"set rnu                 " display relative line numbers
"set nowrap              " do not wrap long lines in display
set nojoinspaces        " do not use double-spaces after .!? when joining
"set textwidth=0         " turn off wordwrap while editing
"set incsearch           " incrementally search during / command
set noerrorbells        " switch off annoying error beeps
set novisualbell        " disable the visual bell too
"set colorcolumn=+1,100   " display a bar just after "textwidth" and at 80
" Pretty print options
set printfont=courier:h9
set printoptions=paper:a4,formfeed:y,number:y,left:36pt,right:36pt,top:36pt,bottom:36pt
" Set up filetype syntax highlighting, indenting and folding
if has("syntax")
	syntax sync fromstart " use slow-but-accurate syntax syncing
endif
if has("persistent_undo")
	if glob($HOME . "/.vim/undo") == ""
		if exists("*mkdir")
			call mkdir($HOME . "/.vim/undo", "p", 0700)
		endif
	endif
	if glob($HOME . "/.vim/undo") != ""
		set undodir=$HOME/.vim/undo
		set undofile
		set undolevels=1000
		set undoreload=10000
	endif
endif
if &term =~ "xterm" || &term =~ "screen"
"	if &termencoding == "utf-8"
		set list listchars=tab:»\ ,trail:·,extends:…
"	else
"		set list listchars=tab:>\ ,trail:.,extends:>
"	endif
endif

" vim: set ts=17:

