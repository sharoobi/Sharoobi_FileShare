# Samba Strategy

Windows host machines already expose SMB on port 445, so Dockerized Samba is not the primary path for this Windows-based workstation scaffold.

Recommended production options:

1. Use native Windows SMB shares for LAN Explorer compatibility.
2. Use SFTPGo WebDAV/HTTP/SFTP as the controlled access plane.
3. If moving to a dedicated Linux server later, add a Samba container or host-native Samba service there.

For this scaffold, SMB remains a design track, not an active container.

