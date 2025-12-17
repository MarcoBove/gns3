ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"

ansible workers_windows -i configs/hosts -m shell -a "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt"

10.0.10.12 | UNREACHABLE! => {
    "changed": false,
    "msg": "Failed to create temporary directory. In some cases, you may have been able to authenticate and did not have permissions on the target directory. Consider changing the remote tmp path in ansible.cfg to a path rooted in \"/tmp\", for more error information use -vvv. Failed command was: ( umask 77 && mkdir -p \"` echo ~/.ansible/tmp `\"&& mkdir \"` echo ~/.ansible/tmp/ansible-tmp-1765935190.4947302-8061-183238679971310 `\" && echo ansible-tmp-1765935190.4947302-8061-183238679971310=\"` echo ~/.ansible/tmp/ansible-tmp-1765935190.4947302-8061-183238679971310 `\" ), exited with result 1",
    "unreachable": true
}
