sudo apt-get update -y --fix-missing
sudo apt-get upgrade -y --fix-missing

sudo apt-get install python3-pip
apt-get install python3-venv

python3 -m venv venv_ESRGAN
source venv_ESRGAN/bin/activate

sudo apt install git

git clone https://github.com/Joseesc24/Proyect_IRSS.git

cd Proyect_IRSS
./installation\ shells/install_requirements.sh

rm -r .git
rm -r irss email module
rm -r irss general functions
rm -r irss image degradation
rm -r irss web interface module
rm -r resources

rm README.md
rm .gitignore
rm install_requirements.sh
