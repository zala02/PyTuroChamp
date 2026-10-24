#!/usr/bin/env python3

# XBoard/UCI interface to PyTuroChamp

# Start with:
# xboard -fcp "python3 xboard.py"

#    Optional debug flags:  -debug -nameOfDebugFile debug.txt -engineDebugOutput 2

from __future__ import print_function

import sys, datetime
import chess as c
import chess.pgn

abc = "abcdefgh"
nn  = "12345678"

is_uci = False

if len(sys.argv) < 2 or sys.argv[1] == 'ptc':
	import pyturochamp as p
	lf = "PyTuroChamp-log.txt"
	mf = "PyTuroChamp.pgn"
	nm = "PyTuroChamp"
elif sys.argv[1] == 'bare':
	import bare as p
	lf = "Bare-log.txt"
	mf = "Bare.pgn"
	nm = "Bare"
else:
	import newt as p
	lf = "Newt-log.txt"
	mf = "Newt.pgn"
	nm = "Newt"

try:
	log = open(lf, 'w')
except:
	log = ''
	print("# Could not create log file")
d = ''
r = ''

def move(r):
    rm = r[0]
    d.push_uci(rm)

    print(f"# DEBUG: is_uci={is_uci}", file=sys.stderr, flush=True)

    if is_uci:
        print("bestmove", rm, flush=True)
    else:
        print("move", rm, flush=True)

    print("# DEBUG: printed move", file=sys.stderr, flush=True)

    if log:
        log.write("move %s\n" % rm)
        log.flush()

    pgn()
    print("# DEBUG: finished move()", file=sys.stderr, flush=True)	
		
def pgn():
	game = chess.pgn.Game.from_board(d)
	now = datetime.datetime.now()
	game.headers["Date"] = now.strftime("%Y.%m.%d")
	if p.pm() > 0:
		game.headers["White"] = nm
		game.headers["Black"] = "User"
	else:
		game.headers["Black"] = nm
		game.headers["White"] = "User"
	try:
		with open(mf, 'w') as f:
			f.write(str(game) + '\n\n\n')
	except:
		print("# Could not write PGN file")

def newgame():
	global d

	d = c.Board()

def fromfen(fen):
	global d

	try:
		d = c.Board(fen)
	except ValueError:
		print("# Bad FEN", file=sys.stderr)

while True:
	l = ''
	try:
		if sys.version < '3':
			l = raw_input()
		else:
			l = input()
	except KeyboardInterrupt:	# XBoard sends Control-C characters, so these must be caught
		if not is_uci:
			pass		#   Otherwise Python would quit.
	if l:
		if log:
			log.write(l + '\n')
			log.flush()
		if l == 'xboard':
			print('feature myname="%s" setboard=1 done=1' % nm)
		elif l == 'quit':
			sys.exit(0)
		elif l == 'new':
			newgame()
		elif l == 'uci':
			is_uci = True
			print("id name", nm)
			print("id author PyTuroChamp")
			print("uciok")
		elif l == 'ucinewgame':
			newgame()
		elif l.startswith('position '):
        		parts = l.split()

	        	if parts[1] == 'startpos':
	                	newgame()
	                	moves_idx = 3

	        	elif parts[1] == 'fen':
        	        	fen_end = parts.index('moves') if 'moves' in parts else len(parts)
                		fen = ' '.join(parts[2:fen_end])
                		fromfen(fen)
                		moves_idx = fen_end + 1

        		else:
                		continue

        		if 'moves' in parts:
                		for mo in parts[moves_idx:]:
                	        	d.push_uci(mo)
		elif l == 'isready':
			print("readyok")
		elif 'setboard' in l:
			fen = l.split(' ', 1)[1]
			fromfen(fen)

		elif l[:2] == 'go' or l == 'force':
				if not d:
						newgame()

				print("# DEBUG: starting getmove", file=sys.stderr, flush=True)
				t, r = p.getmove(d, silent=True)
				print(f"# DEBUG: getmove returned r={r!r}", file=sys.stderr, flush=True)

				if r:
						print("# DEBUG: calling move()", file=sys.stderr, flush=True)
						move(r)
				else:
						print("# DEBUG: no move returned", file=sys.stderr, flush=True)

		elif l == '?':
			print("move", r)
			if log:
				log.write("move %s\n" % r)
				log.flush()
		else:
			if not d:
				newgame()
			if l[0] in abc and l[2] in abc and l[1] in nn and l[3] in nn:
				if len(l) == 6:
					l = l[:4] + 'q'	# "Knights" outputs malformed UCI pawn promotion moves
				d.push_uci(l)
				pgn()
				t, r = p.getmove(d, silent = True)
				if r:
					move(r)


