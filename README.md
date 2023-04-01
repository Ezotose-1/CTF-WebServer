
# CTF-WebServer

Web Server to deploy a 'Capture The Flags'.
Modulable web CTF challenge.

It have been created for student event in **EPITA** IT engineer school.

Build using python 3.10.6

## Installation

Install using Python/Pip

Clone the repo
```bash
git clone git@github.com:Ezotose-1/CTF-WebServer.git
```

Follow these commands to install Python requirements
```bash
python -m venv venv   
. ./venv/bin/activate
python -m pip install --upgrade setuptools pip
python -m pip install -r requirements.txt
```
## Deployment

### Database
In `./tools/postgresql/` Launch the second database :
```bash
docker-compose up [-d :deamonize]
```

### Web server
In the root directory run the web server :
```bash
./src/app.py
```

### SSH access
In your server, create a new user 'user' with a weak password *(such as `password` or any `rockyou.txt` pass)*. And set the shell to the fake 42sh python script in `./tools/tiny_42sh`.

### Non-auto generated flags
Regenerate these 3 elements to change the flag : 
 - **favicon :**
 Go to `./tools/imageCrypto` and change the flag in `binflag.c` and you can generate the favicon with `bindump.py` file.
 - **ssh-weak-passwd :**
 Set the SSH access as decribe before.
 - **reverse-bin :**
 In `./tools/reverse/` change the `reverseme.c` file and run the `build.sh` script to regenerate the `.zip`. Place `project.zip` in `src/static/`.
