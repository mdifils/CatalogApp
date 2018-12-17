# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-18.04"
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
  config.vm.provider "virtualbox" do |vb|
    # customize the name that appears in the VirtualBox GUI
    vb.name = "BionicBeaver"
  end
  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get -y install python3-pip
    sudo pip3 install flask flask-login flask-sqlalchemy flask-migrate
    sudo pip3 install oauth2client requests
  SHELL

end
