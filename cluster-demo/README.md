# Cluster Demo

This Ansible playbook deploys a simple cluster of servers. The cluster is designed as follows:

1). Server #1: DNS server #1; DHCP server #1.
2). Server #2: DNS server #2 (backup); DHCP server #2 (backup).
3). Server #3: OpenVPN CA server.
4). Server #4: OpenVPN server.
4). Server #4: Development server

Notes:

1). All servers have NTP installed to synchronize the time.
