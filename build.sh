
sudo apt update
sudo apt upgrade
sudo apt install virtualenv python3-virtualenv libpq-dev python3-dev build-essential supervisor nginx binutils libproj-dev gdal-bin gettext libgettextpo-dev
adduser pesaify
su - pesaify
virtualenv -p python3 pesaify-business
cd pesaify-business
source bin/activate
mkdir logs
touch logs/gunicorn_supervisor.log
touch logs/nginx-access.log
touch logs/nginx-error.log
git clone https://pesaify@bitbucket.org/pesaify/pesaify-business/
git config --global user.email "admin@pesaify.com"
git config --global user.name "Pesaify"
cd pesaify-business
mv .env.example .env
mv settings/local.py.example settings/local.py
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_user
python manage.py compilemessages
python manage.py collectstatic
exit
cd /home/pesaify/pesaify-business/pesaify-business/
mv .supervisor/pesaify-business.conf /etc/supervisor/conf.d/pesaify-business.conf
sudo chmod u+x .gunicorn/gunicorn_start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status pesaify-business
sudo supervisorctl stop pesaify-business
sudo supervisorctl start pesaify-business
sudo supervisorctl restart pesaify-business
sudo service nginx start
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx
sudo certbot --nginx -d business.pesaify.com
sudo certbot renew
mv .nginx/pesaify-business /etc/nginx/sites-available/pesaify-business
sudo ln -s /etc/nginx/sites-available/pesaify-business /etc/nginx/sites-enabled/pesaify-business
sudo fuser -k 443/tcp
sudo fuser -k 80/tcp
sudo service nginx restart
# rm /etc/nginx/sites-enabled/pesaify-business
