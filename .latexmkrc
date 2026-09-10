# Build the canonical manuscript from the repository root.
$out_dir = 'paper/build';
# Keep forward and inverse search available after command-line builds.
$lualatex = 'lualatex -synctex=1 %O %S';
