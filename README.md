# Instafarm Python 3 Async API

```
.___                 __          _____                      
|   | ____   _______/  |______ _/ ____\____ _______  _____  
|   |/    \ /  ___/\   __\__  \\   __\\__  \\_  __ \/     \ 
|   |   |  \\___ \  |  |  / __ \|  |   / __ \|  | \/  Y Y  \
|___|___|  /____  > |__| (____  /__|  (____  /__|  |__|_|  /
         \/     \/            \/           \/            \/
```

# Setting up the instafarm API service on Linux

Install Nginx
```
$ sudo apt update
$ sudo apt install nginx
```
Configure Nginx Sanic API path:
```
$ nano /etc/nginx/sites-available/default
```

Place the following code to the config file:
```
location /api/ {
        proxy_pass http://localhost:8383;
}

location /swagger/ {
        proxy_pass http://localhost:8383;
}
```
Restart the Nginx service
```
$ sudo service nginx restart
```

### Creating the instafarm service:
```
$ sudo nano /etc/systemd/system/instafarm.service
```
Place the following code to the service file:
```
[Unit]
Description=Instafarm service

[Service]
Type=simple
User=ubuntu
ExecStart=bash /home/ubuntu/sanic/launch.sh

[Install]
WantedBy=multi-user.target
```

### Staging server
http://168.138.131.32/swagger/#/

### Assets packages used at the staging server
https://danaida.itch.io/free-growing-plants-pack-32x32

