# 遇到错误马上停下来
# 显示执行哪一行
set -ex


# 系统设置
apt-get -y install zsh curl ufw
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
ufw allow 22
ufw allow 80
ufw allow 443
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# 装依赖
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update

debconf-set-selections database_secret.conf

apt-get install -y git supervisor nginx python3.6 mysql-server
python3.6 /root/BBS/get-pip.py
pip3 install jinja2 flask gunicorn pymysql flask_sqlalchemy flask_mail flask_socketio

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default

# supervisor
cp /root/BBS/BBS.conf /etc/supervisor/conf.d/BBS.conf
# nginx
# 不要在 sites-available 里面放任何东西
cp /root/BBS/BBS.nginx /etc/nginx/sites-enabled/BBS

# 初始化
cd /root/BBS
python3.6 reset.py

# 重启服务器
service supervisor restart
service nginx restart

echo 'deploy success'