backupr
=========

A backup runner designed to tar up a root directory, optionally encrypt it, and upload to offsite backup.

Requirements
------------

Ensure there is a vault file that imports the following variables
into the ansible runtime environment so we we have proper credentials
to read and write to your desired b2 bucket.

b2_application_key: xxx
b2_application_key_id: xxx

You should also copy the example my_vars.yml.ex file from here to the playbook
using this role and fill in the critical details.


Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

No role dependencies.
Requires `backupr` python pkg.

Example Playbook
----------------

TODO

License
-------

Apache-2.0

Author Information
------------------

Erik Nelson <erik@nsk.io>
