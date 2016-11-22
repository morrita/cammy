Cammy, is a Python project aimed at using a respberry pi as a security camera by providing email alerts and integration with Dropbox.

Installation Instructions:

1) install components in /usr/local/bin/cammy

2) configure the init scripting: 

sudo cp /usr/local/bin/cammy/cammy.sh /etc/init.d
sudo chmod 755 /etc/init.d/cammy.sh
sudo update-rc.d cammy.sh defaults
update-rc.d: using dependency based boot sequencing

3) configure /usr/local/bin/cammy/cammy.ini

4) install Python libraries: 
pip install dropbox

5) sudo apt-get install -y gpac
