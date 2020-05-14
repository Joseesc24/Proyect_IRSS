
actualizar(){
sudo apt-get update -y --fix-missing
sudo apt-get upgrade -y --fix-missing
sudo apt-get dist-upgrade -y --fix-missing
sudo apt-get check -y
sudo apt --fix-broken -y install
sudo apt autoremove -y --purge
sudo apt autoremove -y
sudo apt autoclean -y
sudo apt remove -y
sudo apt clean -y
}

actualizar
sudo apt-get install python3-pip -y
apt-get install python3-venv -y
actualizar
sudo apt-get install python3-pip
actualizar
sudo pip3 install virtualenv

virtualenv -p python3 TecoGAN
cd TecoGAN
git clone https://github.com/thunil/TecoGAN.git
cd TecoGAN
source bin/activate
pip3 install wrapt --upgrade --ignore-installed
pip3 install --upgrade pip
pip3 install tensorflow==1.14.0 --upgrade --ignore-installed
pip3 install -r requirements.txt
pip3 install ipython==4.0.2 --upgrade --ignore-installed
pip3 install prompt_toolkit==1.0.18 --upgrade --ignore-installed
pip3 uninstall --yes ipython==7.13.0
pip3 install -r requirements.txt
python3 runGan.py 0
python3 runGan.py 1
