# LoL Optimizer deployment

## Set up

From this directory `./dev`.

```
cp /terraform/terraform.tfvars.template terraform/terraform.tfvars
```

Edit the values with `vim` or `nano` with your tenancy, compartment, ssh public key and Riot API key:
```
vim terraform/terraform.tfvars
```

## Deploy

```
./start.sh
```

After few minutes, you will be asked:

```
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Type `yes` and enter.

> Problems?
> If you take some time to answer `yes`, ansible will timeout with the following error message.
> ```
> fatal: [node1]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Warning: Permanently added 'x.x.x.x' (ED25519) to the list of known hosts.\r\nConnection closed by x.x.x.x port 22", "unreachable": true}
> ```
>
> Run `.start.sh` again.

The output will be an `ssh` command to connect with the machine.

### Destroy

```
./stop.sh
```
