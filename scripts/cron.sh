#PROJECT_HOME=/home/manish/imly/
PROJECT_HOME=/root/imly/
cd $PROJECT_HOME
#source /home/manish/imly_envi/bin/activate
python manage.py imly_reset_stocks
python manage.py flag_products_mail