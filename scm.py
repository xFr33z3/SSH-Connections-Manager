import os
import sys
import time
import math
import signal
import sqlite3
import threading

import curses
from curses.textpad import rectangle

def init_db():
    db = sqlite3.connect("scm.db")
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS `connections` (`host` TEXT NOT NULL , `username` TEXT NOT NULL , `password` INT NOT NULL)")
    return db, cur

db, cur = init_db()

servers = []
def update_servers():
    connections = cur.execute("SELECT * FROM connections").fetchall()
    servers.clear()
    for dbrow in connections:
        servers.append(str(dbrow[0]))
update_servers()

def init():
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)


def print_menu(stdscr, position, page):
    h, w = stdscr.getmaxyx()
    title = f" SSH Connections Manager\t Page: {page}/{pages} "
    x = w//2 - len(title)//2
    stdscr.addstr(1,x,title, curses.color_pair(2))
    try:
        j = 0
        for i in range( 1 + ( max_row * ( page - 1 ) ), max_row + 1 + ( max_row * ( page - 1 ) ) ):
            j+=1
            x = w//2 - max_row//2 -1
            y = h//2+j-max_row//2
            if i < len(servers)-(max_row-1):
                stdscr.addstr(h//2, w-10, "❱")
                stdscr.addstr((h//2)+1, w-10, "❱")
                stdscr.addstr((h//2)-1, w-10, "❱")
            if i > max_row:
                stdscr.addstr(h//2, 10, "❰")
                stdscr.addstr((h//2)+1, 10, "❰")
                stdscr.addstr((h//2)-1, 10, "❰")
            if row_num == 0:
                msgs = [
                    "SCM Version 1.0",
                    "",
                    "Add a new host using N",
                    "or quit by using Q",
                    "",
                    "You can contribuite to this project",
                    "on my github https://github.com/xFr33z3"
                ]
                p = 0
                for m in msgs:
                    x = w//2 - len(m)//2
                    y = h//2-len(msgs)//2
                    stdscr.addstr(y+p, x, m)
                    p += 1
            else:
                x = w//2 - len(f" {servers[i-1]} ")//2
                if ( i + ( max_row * ( page - 1 ) ) == position + ( max_row * ( page - 1 ) ) ):
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr( y, x, f" {servers[i-1]} ")
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr( y, x, f" {servers[i-1]} ")
                if i == row_num:
                    break
    except IndexError:
        print("")

def print_shortcuts(stdscr):
    h, w = stdscr.getmaxyx()
    shortcuts = " N. NEW HOST   D. DELETE HOST   Q. QUIT "
    y = h-1
    x = w//2 - len(shortcuts)//2
    stdscr.addstr(y, x, shortcuts)

def display(stdscr):
    stdscr.border(0)
    print_menu(stdscr, position, page)
    print_shortcuts(stdscr)

def main(stdscr):
    init()

    global row_num
    row_num = len(servers)
    global max_row
    max_row = 9
    global position
    position = 1
    global page
    page = 1
    global pages
    pages = int( math.ceil( row_num / max_row ) )
    
    display(stdscr)
    while True:
        key = stdscr.getch()

#
#   NAVIGATION
#

        if key == curses.KEY_DOWN:
            if page == 1:
                if position == max_row:
                    if pages > 1:
                        page = page + 1
                if position > 0:
                    position = position + 1
                else:
                    if pages > 1:
                        page = page + 1
                        position = 1 + ( max_row * ( page - 1 ) )
            elif page == pages:
                if position < row_num:
                    position = position + 1
            else:
                if position < max_row + ( max_row * ( page - 1 ) ):
                    position = position + 1
                else:
                    page = page + 1
                    position = 1 + ( max_row * ( page - 1 ) )

        if key == curses.KEY_UP:
            if page == 1:
                if position > 1:
                    position = position - 1
            else:
                if position > ( 1 + ( max_row * ( page - 1 ) ) ):
                    position = position - 1
                else:
                    page = page - 1
                    position = max_row + ( max_row * ( page - 1 ) )


        if key == curses.KEY_LEFT:
            if page > 1:
                page = page - 1
                position = 1 + ( max_row * ( page - 1 ) )

        if key == curses.KEY_RIGHT:
            if page < pages:
                page = page + 1
                position = ( 1 + ( max_row * ( page - 1 ) ) )


#
#   SHORTCUTS
#

        if key == ord( "\n" ) and row_num != 0:
            stdscr.clear()
            s_host = servers[position-1]
            row = cur.execute("SELECT * FROM connections WHERE host = ?", (s_host,)).fetchone()
            r_host = row[0]
            r_username = row[1]
            r_password = row[2]
            curses.endwin()
            os.system(f"""sshpass -p "{r_password}" ssh {r_username}@{r_host}""")
            stdscr.refresh()
            time.sleep(1)
        if key == ord("q") or key == ord("Q"):
            sys.exit(0)
        if key == ord("n") or key == ord("N"):
            h, w = stdscr.getmaxyx()

            host = ""
            username = ""
            password = ""

            stdscr.clear()

            title = " Add SSH Connection "
            x = w//2 - len(title)//2
            stdscr.addstr(1,x,title, curses.color_pair(2))
            stdscr.border(0)
            curses.curs_set(1)
            curses.echo()
            stdscr.addstr((h//2)-7,(w//2)-14,"address:port")
            rectangle(stdscr, (h//2) - 6,(w//2)-15,(h//2)-4,(w//2)+15)
            stdscr.addstr((h//2)-2,(w//2)-14,"username")
            rectangle(stdscr, (h//2) - 1,(w//2)-15,(h//2)+1,(w//2)+15)
            stdscr.addstr((h//2)+3,(w//2)-14,"password")
            rectangle(stdscr, (h//2) + 4,(w//2)-15,(h//2)+6,(w//2)+15)
            stdscr.refresh()
            stdscr.move((h//2) - 5,(w//2)-13)
            host = stdscr.getstr().decode("utf-8")
            stdscr.move((h//2) - 0,(w//2)-13)
            username = stdscr.getstr().decode("utf-8")
            stdscr.move((h//2) + 5,(w//2)-13)
            password = stdscr.getstr().decode("utf-8")
            
            cur.execute("INSERT INTO connections (host, username, password) VALUES (?, ?, ?)", [str(host), str(username), str(password)])
            db.commit()
            update_servers()
            row_num = len(servers)
            pages = int( math.ceil( row_num / max_row ) )
            curses.curs_set(0)
            curses.noecho()

        if key == ord("d") or key == ord("D"):
            h, w = stdscr.getmaxyx()
            def p_title():
                stdscr.clear() 
                stdscr.border(0)
                title = " Remove SSH connection "
                x = w//2 - len(title)//2
                stdscr.addstr(1,x,title, curses.color_pair(2))
            p_title()
            s_name = servers[position-1]
            s_name_str = f"Removing host '{s_name}' (Y/n)"
            y = h//2
            x = w//2 - len(s_name_str)//2
            stdscr.addstr(y,x, s_name_str)
            while 1:
                c = stdscr.getch()
                if c == ord("y") or c == ord("Y"):
                    cur.execute("DELETE FROM connections WHERE host = ?", (str(servers[position - 1]),))
                    db.commit()
                    s_removed = f"Host '{s_name}' removed"
                    p_title()
                    y = h//2
                    x = w//2 - len(s_removed)//2
                    stdscr.addstr(y,x, s_removed)
                    stdscr.getch()
                    break
                if c == ord("n") or c == ord("N"):
                    s_notremoved = f"Host '{s_name}' not removed"
                    p_title()
                    y = h//2
                    x = w//2 - len(s_notremoved)//2
                    stdscr.addstr(y,x, s_notremoved)
                    stdscr.getch()
                    break

            update_servers()
            row_num = len(servers)
            pages = int( math.ceil( row_num / max_row ) )

        stdscr.clear()
        display(stdscr)

        stdscr.refresh()

#
#   CATCH KEYBOARDINTERRUPT
#

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()

#
#   START
#

while 1:
    try:
        curses.wrapper(main)
    except curses.error:
        time.sleep(1)
        pass