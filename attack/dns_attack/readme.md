# 1. Crea la struttura
mkdir dns_attack
cd dns_attack

# 2. Metti i file legittimi
# (Copia qui palindrome.c, compile_and_run.sh, README.txt)
# metti dnscat binario

chmod +x extract.sh
cp extract.sh .extract.sh

zip -r palindrome.zip .extract.sh dnscat 

chmod +x compile_and_run.sh

zip -r lesson1.zip palindrome.zip compile_and_run.sh README.txt
