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

    wallet.vm.network "forwarded_port", guest: 80, host: 9000
    wallet.vm.network "private_network", type: "dhcp"

    wallet.vm.synced_folder ".", "/vagrant", type: "nfs"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbooks/bootstrap.yml"
    ansible.tags = ANSIBLE_TAGS
    ansible.extra_vars = {
        ansible_ssh_user: 'vagrant',

        cluster_environment: 'vagrant',
        common_user: 'clayman',
        common_user_password: '$6$rounds=100000$.8T6PFb3OsCTxhhx$lEW5mbxgI5wTBA5NU27iB51YeI./ljG9tlkygQ6NOwIRAMuS8qnp3UAqEQNO5hTI5OaDxFL6XLJQSh67qAEkO0',

        project_user: 'clayman',
        project_name: 'wallet',
        project_domain: 'wallet.clayman.pro',
        project_socket: '127.0.0.1:5000',
        project_venv: '/vagrant',
        project_assets: '/vagrant/wallet',
        project_media: '/vagrant/wallet',
    }
  end
end
