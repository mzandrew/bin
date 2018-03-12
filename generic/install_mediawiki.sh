#!/bin/bash -e

# written 2017-08-31 by mza
# based off a script from Anh Lam

# https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-on-centos-7
# https://www.digitalocean.com/community/tutorials/how-to-install-mediawiki-on-centos-7

#sudo yum -y install texlive # for rendering latex markup
#sudo yum -y install php-xml php-intl php-xcache
#sudo yum -y install ImageMagick # for image thumbnailing
#sudo yum -y install php-mysql
#sudo yum -y install mariadb mariadb-server # backend mysql database
#sudo yum -y install mediawiki123 mediawiki123-doc # wiki
#sudo yum -y install httpd # apache web server

#sudo systemctl enable httpd
#sudo systemctl start httpd
#sudo systemctl enable mariadb
#sudo systemctl start mariadb
#mysqladmin status # Uptime: 543  Threads: 1  Questions: 2  Slow queries: 0  Opens: 0  Flush tables: 2  Open tables: 26  Queries per second avg: 0.003

#sudo iptables -A INPUT -s 192.168.153.0/24 -p tcp --dport http -j ACCEPT # accept incoming web/http (dport 80)
#sudo mv /var/www/mediawiki123 /var/www/html/wiki

#mysqladmin -u root password # prompts for new password for mysqladmin "root" user

#mysql -u root -p
#create database wiki;
#GRANT INDEX, CREATE, SELECT, INSERT, UPDATE, DELETE, ALTER, LOCK TABLES ON wiki.* TO 'admin'@'localhost' IDENTIFIED BY '*******';
#exit;

# mysql settings: host=localhost, name=wiki, table_prefix="", username=admin, password=*******
# name=IDLAB wiki, namespace=IDLAB
# private_wiki, no_license_footer, enable_file_uploads
# download LocalSettings.php, move to /var/www/html/wiki, chown apache:apache LocalSettings.php, then
#sudo restorecon -v /var/www/html/wiki/LocalSettings.php
#sudo setsebool -P httpd_can_sendmail on

sudo yum -y install postfix
# add line "myhostname = blah" to /etc/postfix/main.cf
sudo systemctl start postfix
sudo systemctl enable postfix
#netstat -lnt | grep :25
sudo alternatives --config mta # select sendmail.postfix; test by issuing "sendmail you@yours" and seeing if it works

# common pitfalls:
# if it fails with "Could not find a suitable database driver!" even after installing php-mysql, then you need to restart apache
# if it can't send email "IDLAB wiki could not send your confirmation mail. Please check your email address for invalid characters.  Mailer returned: Unknown error in PHP's mail() function.", then do "sudo setsebool -P httpd_can_sendmail on", but that doesn't fix it.  "sudo semanage permissive -a httpd_t" also doesn't fix it.  Adding a "mail" entry to the .128 line in /etc/hosts also doesn't fix it "sendmail you@yours test sendmail: Cannot open mail:25" - have to do "alternatives --config mta"

# edit wiki/index.php/MediaWiki:Sidebar to customize the left-hand sidebar

