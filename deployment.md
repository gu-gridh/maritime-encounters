# Installation:
python3.12  -m venv maritime
pip install -r requirements.txt

on server number 3
/etc/httpd/conf.d/

then on server 2
/etc/systemd/system/app.service 
sudo systemctl start maritime

on server 3
sudo systemctl restart httpd

open the port manually on cdh02