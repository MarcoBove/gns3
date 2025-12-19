ssh osboxes@10.0.20.10 "export DISPLAY=:0 && firefox https://www.google.com"

ssh User@10.0.10.12 "echo https://www.google.com > C:/Users/User/dapt2021/worker/current_url.txt && schtasks /run /tn DaptBrowser"

ansible workers_windows -i configs/hosts -m raw -a "cmd /c echo https://www.google.com > C:\Users\User\dapt2021\worker\current_url.txt"

ansible workers_windows -i configs/hosts -m raw -a "schtasks /run /tn DaptBrowser"

C:\Users\User\dapt2021\worker\run_task.bat https://www.repubblica.it

ansible workers_windows -i configs/hosts -m raw -a "C:\Users\User\dapt2021\worker\run_task.bat https://www.google.com"




export TMPDIR=/home/student/tmp_firefox && /home/student/user_behavior_generation/worker/venv/bin/python /home/student/user_behavior_generation/worker/smart_worker.py https://www.google.com generic


ssh student@10.0.20.10 "export DISPLAY=:0 && export TMPDIR=/home/student/tmp_firefox && /home/student/user_behavior_generation/worker/venv/bin/python /home/student/user_behavior_generation/worker/smart_worker.py https://www.google.com generic"
[OPEN] https://www.google.com
[CRAWL] Cerco link... Depth: 2
[CRAWL] Clicco su: https://store.google.com/IT?utm_source=hp_header&utm_medium=google_ooo&utm_campaign=GS100042&hl=it-IT
[CRAWL] Cerco link... Depth: 1
[CRAWL] Clicco su: https://store.google.com/it/config/pixel_10?hl=it
[DONE] Sessione finita.
