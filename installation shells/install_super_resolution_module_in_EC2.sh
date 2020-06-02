sudo apt-get update -y --fix-missing
sudo apt-get upgrade -y --fix-missing

sudo apt-get -y install python3-pip
sudo apt-get -y install python3-venv

python3 -m venv venv_ESRGAN
source venv_ESRGAN/bin/activate

sudo apt -y install git
sudo apt-get -y install python3-pip

git clone https://github.com/Joseesc24/Proyect_IRSS.git

cd Proyect_IRSS
./installation\ shells/install_requirements.sh

rm -rf .git
rm -rf irss email module
rm -rf irss general functions
rm -rf irss image degradation
rm -rf irss web interface module
rm -rf resources

rm README.md
rm .gitignore
rm install_requirements.sh
