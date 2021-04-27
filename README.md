# wp-permissions

### Example 1:

**Runs on all domains found in the `--webroot` and sets the permissions to be strict.**

`python3 main.py --webroot /var/www --siteroot html/ --web-user www-data --admin-user serveradmin --level 1`


### Example 2:

**Runs on all domains found in the `--webroot` and sets the permissions to be relaxed (useful for updating/installing plugins).**

`python3 main.py --webroot /var/www --siteroot html/ --web-user www-data --admin-user serveradmin --level 2`

### Example 3:

**Runs on a specific domain**

`python3 main.py --webroot /var/www --siteroot html/ --web-user www-data --admin-user serveradmin --domain website.com --level 1`
