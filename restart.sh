
pkill nginx
pkill python

cp /var/eightlegs.tv/nginx.conf /etc/nginx/

python /var/eightlegs.tv/app/__init__.py 8000&
python /var/eightlegs.tv/app/__init__.py 8001&
python /var/eightlegs.tv/app/__init__.py 8002&
python /var/eightlegs.tv/app/__init__.py 8003&

/etc/init.d/nginx start
