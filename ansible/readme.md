ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"

ansible workers_windows -i configs/hosts -m shell -a "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt"

10.0.10.12 | UNREACHABLE! => {
    "changed": false,
    "msg": "Failed to create temporary directory. In some cases, you may have been able to authenticate and did not have permissions on the target directory. Consider changing the remote tmp path in ansible.cfg to a path rooted in \"/tmp\", for more error information use -vvv. Failed command was: ( umask 77 && mkdir -p \"` echo ~/.ansible/tmp `\"&& mkdir \"` echo ~/.ansible/tmp/ansible-tmp-1765935190.4947302-8061-183238679971310 `\" && echo ansible-tmp-1765935190.4947302-8061-183238679971310=\"` echo ~/.ansible/tmp/ansible-tmp-1765935190.4947302-8061-183238679971310 `\" ), exited with result 1",
    "unreachable": true
}

[WARN] Windows Command FAILED!
--- STDOUT: ---
10.0.10.12 | FAILED! => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "module_stderr": "Parameter format not correct - ;\r\n",
    "module_stdout": "",
    "msg": "MODULE FAILURE\nSee stdout/stderr for the exact error",
    "rc": 1
}

--- STDERR: ---
[WARNING]: Unhandled error in Python interpreter discovery for host 10.0.10.12:
unexpected output from Python interpreter discovery
[WARNING]: Platform unknown on host 10.0.10.12 is using the discovered Python
interpreter at /usr/bin/python, but future installation of another Python
interpreter could change the meaning of that path. See
https://docs.ansible.com/ansible-
core/2.16/reference_appendices/interpreter_discovery.html for more information.
