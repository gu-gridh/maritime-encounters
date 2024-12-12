<VirtualHost *:80>
    ServerName maritime-encounters.dh.gu.se
    RewriteEngine On
    RewriteCond %{HTTPS} !on
    RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}
</VirtualHost>

<VirtualHost *:443>
    SSLEngine On
    SSLCertificateFile /etc/httpd/conf/cert/__dh_gu_se_cert.cer
    SSLCertificateKeyFile /etc/httpd/conf/key/*.dh.gu.se.pem
    SSLCertificateChainFile /etc/httpd/conf/cert/__dh_gu_se_interm.cer

 DocumentRoot /var/www/html2/maritime
<Directory "/var/www/html2/maritime/">
   # run the whole thing behind authentication
   AuthType Basic
   AuthName "Restricted Access"
   AuthUserFile "/var/www/htpasswd"
        Require user maritime
        AllowOverride All
        #Require all granted
</Directory>

    ServerName maritime-encounters.dh.gu.se

    # Django Backend running on cdh02
    RequestHeader set X-Forwarded-Proto https
    ProxyPreserveHost On
    ProxyPass        /static !

    #Alias            /static/ /data/cdhdata/public/maritime-enconters/static/static_build/
    #ProxyPass        / http://gridh06-p.gu.gu.se:8095/
    #ProxyPassReverse / http://gridh06-p.gu.gu.se:8095/
    Alias            /static/ /data/cdhdata/public/maritime-enconters/static/static_build/

     ProxyPass        /api http://gridh06-p.gu.gu.se:8095/api Keepalive=On retry=2 acquire=90
     ProxyPassReverse /api http://gridh06-p.gu.gu.se:8095/api
     ProxyPass        /admin http://gridh06-p.gu.gu.se:8095/admin Keepalive=On retry=2 acquire=90
     ProxyPassReverse /admin http://gridh06-p.gu.gu.se:8095/admin


    ProxyTimeout 60000

    ErrorLog  /var/log/httpd/maritime.error.log
    LogLevel  info
    CustomLog /var/log/httpd/maritime.access.log combined

</VirtualHost>

