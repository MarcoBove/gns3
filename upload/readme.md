osboxes@osboxes:~/Desktop/ansible$ ssh -v Student@10.0.10.12
OpenSSH_9.6p1 Ubuntu-3ubuntu13.14, OpenSSL 3.0.13 30 Jan 2024
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: /etc/ssh/ssh_config line 19: include /etc/ssh/ssh_config.d/*.conf matched no files
debug1: /etc/ssh/ssh_config line 21: Applying options for *
debug1: Connecting to 10.0.10.12 [10.0.10.12] port 22.
debug1: Connection established.
debug1: identity file /home/osboxes/.ssh/id_rsa type 0
debug1: identity file /home/osboxes/.ssh/id_rsa-cert type -1
debug1: identity file /home/osboxes/.ssh/id_ecdsa type -1
debug1: identity file /home/osboxes/.ssh/id_ecdsa-cert type -1
debug1: identity file /home/osboxes/.ssh/id_ecdsa_sk type -1
debug1: identity file /home/osboxes/.ssh/id_ecdsa_sk-cert type -1
debug1: identity file /home/osboxes/.ssh/id_ed25519 type -1
debug1: identity file /home/osboxes/.ssh/id_ed25519-cert type -1
debug1: identity file /home/osboxes/.ssh/id_ed25519_sk type -1
debug1: identity file /home/osboxes/.ssh/id_ed25519_sk-cert type -1
debug1: identity file /home/osboxes/.ssh/id_xmss type -1
debug1: identity file /home/osboxes/.ssh/id_xmss-cert type -1
debug1: identity file /home/osboxes/.ssh/id_dsa type -1
debug1: identity file /home/osboxes/.ssh/id_dsa-cert type -1
debug1: Local version string SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.14
debug1: Remote protocol version 2.0, remote software version OpenSSH_for_Windows_8.6
debug1: compat_banner: match: OpenSSH_for_Windows_8.6 pat OpenSSH* compat 0x04000000
debug1: Authenticating to 10.0.10.12:22 as 'Student'
debug1: load_hostkeys: fopen /home/osboxes/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug1: SSH2_MSG_KEXINIT sent
debug1: SSH2_MSG_KEXINIT received
debug1: kex: algorithm: curve25519-sha256
debug1: kex: host key algorithm: ssh-ed25519
debug1: kex: server->client cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug1: kex: client->server cipher: chacha20-poly1305@openssh.com MAC: <implicit> compression: none
debug1: expecting SSH2_MSG_KEX_ECDH_REPLY
debug1: SSH2_MSG_KEX_ECDH_REPLY received
debug1: Server host key: ssh-ed25519 SHA256:vWFliYIp9GmAQG2h6XtU6zA+eilCQixdLODmlK5MJ2I
debug1: load_hostkeys: fopen /home/osboxes/.ssh/known_hosts2: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts: No such file or directory
debug1: load_hostkeys: fopen /etc/ssh/ssh_known_hosts2: No such file or directory
debug1: Host '10.0.10.12' is known and matches the ED25519 host key.
debug1: Found key in /home/osboxes/.ssh/known_hosts:14
debug1: rekey out after 134217728 blocks
debug1: SSH2_MSG_NEWKEYS sent
debug1: expecting SSH2_MSG_NEWKEYS
debug1: SSH2_MSG_NEWKEYS received
debug1: rekey in after 134217728 blocks
debug1: SSH2_MSG_EXT_INFO received
debug1: kex_ext_info_client_parse: server-sig-algs=<ssh-ed25519,sk-ssh-ed25519@openssh.com,ssh-rsa,rsa-sha2-256,rsa-sha2-512,ssh-dss,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,sk-ecdsa-sha2-nistp256@openssh.com,webauthn-sk-ecdsa-sha2-nistp256@openssh.com>
debug1: SSH2_MSG_SERVICE_ACCEPT received
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug1: Next authentication method: publickey
debug1: get_agent_identities: bound agent to hostkey
debug1: get_agent_identities: agent returned 1 keys
debug1: Will attempt key: /home/osboxes/.ssh/id_rsa RSA SHA256:2IGPpzXeYsaJsOr7oPK5hQL+D7gozUQggLfp7zTsnZg agent
debug1: Will attempt key: /home/osboxes/.ssh/id_ecdsa 
debug1: Will attempt key: /home/osboxes/.ssh/id_ecdsa_sk 
debug1: Will attempt key: /home/osboxes/.ssh/id_ed25519 
debug1: Will attempt key: /home/osboxes/.ssh/id_ed25519_sk 
debug1: Will attempt key: /home/osboxes/.ssh/id_xmss 
debug1: Will attempt key: /home/osboxes/.ssh/id_dsa 
debug1: Offering public key: /home/osboxes/.ssh/id_rsa RSA SHA256:2IGPpzXeYsaJsOr7oPK5hQL+D7gozUQggLfp7zTsnZg agent
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug1: Trying private key: /home/osboxes/.ssh/id_ecdsa
debug1: Trying private key: /home/osboxes/.ssh/id_ecdsa_sk
debug1: Trying private key: /home/osboxes/.ssh/id_ed25519
debug1: Trying private key: /home/osboxes/.ssh/id_ed25519_sk
debug1: Trying private key: /home/osboxes/.ssh/id_xmss
debug1: Trying private key: /home/osboxes/.ssh/id_dsa
debug1: Next authentication method: keyboard-interactive
debug1: Authentications that can continue: publickey,password,keyboard-interactive
debug1: Next authentication method: password
Student@10.0.10.12's password: 
Authenticated to 10.0.10.12 ([10.0.10.12]:22) using "password".
debug1: channel 0: new session [client-session] (inactive timeout: 0)
debug1: Requesting no-more-sessions@openssh.com
debug1: Entering interactive session.
debug1: pledge: filesystem
debug1: client_input_global_request: rtype hostkeys-00@openssh.com want_reply 0
debug1: client_input_hostkeys: searching /home/osboxes/.ssh/known_hosts for 10.0.10.12 / (none)
debug1: client_input_hostkeys: searching /home/osboxes/.ssh/known_hosts2 for 10.0.10.12 / (none)
debug1: client_input_hostkeys: hostkeys file /home/osboxes/.ssh/known_hosts2 does not exist
debug1: Sending environment.
debug1: channel 0: setting env LANG = "en_US.UTF-8"
debug1: client_global_hostkeys_prove_confirm: server used untrusted RSA signature algorithm ssh-rsa for key 0, disregarding
debug1: update_known_hosts: known hosts file /home/osboxes/.ssh/known_hosts2 does not exist
debug1: pledge: fork

Microsoft Windows [Version 10.0.22621.2134]
(c) Microsoft Corporation. All rights reserved.

student@WINDEV2308EVAL C:\Users\Student>
