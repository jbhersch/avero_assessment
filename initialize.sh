cd ~
wget http://repo.continuum.io/archive/Anaconda2-4.3.0-Linux-x86_64.sh
bash Anaconda2-4.3.0-Linux-x86_64.sh
source ~/.bashrc
conda update conda
conda install pip
conda install virtualenv

pip install -r requirements.txt
