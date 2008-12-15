#! /bin/sh -e
 
rm -rf reportlab
R=../reportlab
hg clone $R reportlab
id=$(hg ident -i reportlab/)
rsync -aH --delete reportlab/src/reportlab mwlib/
rsync -aH --delete reportlab/src/rl_addons mwlib/
hg addremove mwlib/reportlab
hg addremove mwlib/rl_addons

hg ci -m "addremove version $id of reportlab" mwlib
