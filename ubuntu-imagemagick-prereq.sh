sudo su;

sudo apt install alien
sudo alien -i ImageMagick-libs-7.0.7-37.x86_64.rpm


apt update -qq
apt install --no-install-recommends software-properties-common dirmngr
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
apt install --no-install-recommends r-base
add-apt-repository ppa:c2d4u.team/c2d4u4.0+
ldconfig /usr/local/lib
#optional
apt install --no-install-recommends r-cran-rstan


python color_trace.py ~/aidinstinct/src/assets/images/icons/theme_1/color_trace-0.02/test/ -colors 256 ~/aidinstinct/src/assets/images/icons/theme_1/color_trace-0.02/test-out/