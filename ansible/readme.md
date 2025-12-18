ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"

ansible workers_windows -i configs/hosts -m raw -a "cmd /c echo https://www.google.com > C:\Users\User\dapt2021\worker\current_url.txt"

ansible workers_windows -i configs/hosts -m raw -a "schtasks /run /tn DaptBrowser"





C:\Users\User\dapt2021\worker\run_task.bat https://www.repubblica.it

ansible workers_windows -i configs/hosts -m raw -a "C:\Users\User\dapt2021\worker\run_task.bat https://www.google.com"

student@osboxes:~$ /home/student/user_behavior_generation/worker/venv/bin/python /home/student/user_behavior_generation/worker/smart_worker.py https://www.google.com generic
[ERROR] Driver init failed: Message: Process unexpectedly closed with status 1

student@osboxes:~$ /home/student/user_behavior_generation/worker/venv/bin/python3 /home/student/user_behavior_generation/worker/smart_worker.py https://www.google.com generic
[ERROR] Driver init failed: Message: Process unexpectedly closed with status 1

Mi esce prima un popup : Your Firefox profile cannot be loaded. It may be missing or inaccessible.
