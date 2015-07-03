# -*- mode: ruby -*-
# vi: set ft=ruby :

ANSIBLE_TAGS=ENV['ANSIBLE_TAGS']

Vagrant.configure("2") do |config|
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "512"]
  end

  config.vm.define "wallet" do |wallet|
    wallet.vm.box = "ubuntu/trusty64"
    wallet.vm.hostname = "wallet"

    wallet.vm.network "forwarded_port", guest: 80, host: 8080
    wallet.vm.network "forwarded_port", guest: 6379, host: 6379
    wallet.vm.network "forwarded_port", guest: 5432, host: 5432
    wallet.vm.network "private_network", type: "dhcp"

    wallet.vm.synced_folder ".", "/vagrant", type: "nfs"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbooks/bootstrap.yml"
    ansible.tags = ANSIBLE_TAGS
    ansible.extra_vars = {
        ansible_ssh_user: 'vagrant',

        project_name: 'wallet',
        project_domain: 'wallet.clayman.pro',
        project_socket: '192.168.1.22:5000',
        project_venv: '/vagrant',
        project_assets: '/vagrant/wallet/assets/',
        project_media: '/vagrant/wallet',
    }
  end
end
