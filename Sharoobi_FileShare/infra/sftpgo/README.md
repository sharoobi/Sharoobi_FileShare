# SFTPGo Notes

This directory is mounted into the SFTPGo container as `/var/lib/sftpgo`.

The initial scaffold uses:

- SQLite as isolated provider metadata store
- local storage rooted at `/srv/sftpgo`
- web admin and web client on port `19080`
- SFTP on port `19022`

Recommended next steps:

1. create groups for shares
2. create virtual folders mapped to registered Windows paths or host bridge exports
3. define bandwidth profiles
4. wire event hooks into the control API
