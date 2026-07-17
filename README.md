## Detection VM Service

# Responsibilities:
- Watch incoming files
- Analyze files
- Route files
- Log decisions

Inputs:
- /mnt/incoming

Outputs:
- /mnt/backup_inbox
- /mnt/quarantine

Dependencies:
- watchdog
- analyzer
- router

Not Responsible For:
- backup storage
- restore operations
- user management
- dashboard functionality
