# SSH-Connections-Manager

Simple application written in Python useful for managing and ordering several SSH servers

# Screenshots
![Main page](https://i.imgur.com/uVt1eBv.png)
![Add new SSH server](https://i.imgur.com/FR6roku.png)
![Remove SSH server](https://i.imgur.com/Ecf5QGM.png)

## Install global dependencies
    
### Debian based
    apt install python3 sqlite3 libncurses5-dev libncursesw5-dev sshpass -y
    
### Arch based
    pacman -S python3 sqlite ncurses sshpass

## Usage
Clone this repository using

    git clone https://github.com/xFr33z3/SSH-Connections-Manager.git

Change folder to SSH-Connections-Manager directory

    cd SSH-Connections-Manager
    
Run with

    python3 scm.py
