winrar attack
https://github.com/Syrins/CVE-2025-8088-Winrar-Tool-Gui

https://nvd.nist.gov/vuln/detail/CVE-2025-8088

https://www.youtube.com/watch?v=m_0Axsh_oO4
PS C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main> .\venv\Scripts\python .\gui.py
Traceback (most recent call last):
  File "C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main\gui.py", line 3, in <module>
    import customtkinter as ctk
  File "C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main\venv\Lib\site-packages\customtkinter\__init__.py", line 10, in <module>
    from .windows.widgets.appearance_mode import AppearanceModeTracker
  File "C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main\venv\Lib\site-packages\customtkinter\windows\__init__.py", line 1, in <module>
    from .ctk_tk import CTk
  File "C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main\venv\Lib\site-packages\customtkinter\windows\ctk_tk.py", line 2, in <module>
    from distutils.version import StrictVersion as Version
ModuleNotFoundError: No module named 'distutils'
PS C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main> .\venv\Scripts\activate
(venv) PS C:\Users\Secretary\Desktop\CVE-2025-8088-Winrar-Tool-Gui-main> pip install -r .\requirements.txt
Collecting customtkinter==5.2.0 (from -r .\requirements.txt (line 1))
  Using cached customtkinter-5.2.0-py3-none-any.whl.metadata (652 bytes)
Collecting pycryptodome==3.23.0 (from -r .\requirements.txt (line 2))
  Using cached pycryptodome-3.23.0-cp37-abi3-win_amd64.whl.metadata (3.5 kB)
Collecting darkdetect (from customtkinter==5.2.0->-r .\requirements.txt (line 1))
  Using cached darkdetect-0.8.0-py3-none-any.whl.metadata (3.6 kB)
Using cached customtkinter-5.2.0-py3-none-any.whl (295 kB)
Using cached pycryptodome-3.23.0-cp37-abi3-win_amd64.whl (1.8 MB)
Using cached darkdetect-0.8.0-py3-none-any.whl (9.0 kB)
Installing collected packages: pycryptodome, darkdetect, customtkinter
Successfully installed customtkinter-5.2.0 darkdetect-0.8.0 pycryptodome-3.23.0
