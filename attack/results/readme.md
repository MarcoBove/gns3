
PS C:\Users\User\user_behavior_generation\worker\venv\Scripts> .\activate
(venv) PS C:\Users\User\user_behavior_generation\worker\venv\Scripts> pip install dnspython
Requirement already satisfied: dnspython in c:\users\user\user_behavior_generation\worker\venv\lib\site-packages (2.8.0)
(venv) PS C:\Users\User\user_behavior_generation\worker\venv\Scripts> .\python.exe C:\Users\User\user_behavior_generation\worker\dns.py
Traceback (most recent call last):
  File "C:\Users\User\user_behavior_generation\worker\dns.py", line 6, in <module>
    import dns.resolver # Richiede: pip install dnspython
    ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\User\user_behavior_generation\worker\dns.py", line 6, in <module>
    import dns.resolver # Richiede: pip install dnspython
    ^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'dns.resolver'; 'dns' is not a package
(venv) PS C:\Users\User\user_behavior_generation\worker\venv\Scripts>
