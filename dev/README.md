# LoL Optimizer deployment

## FIX

Python 3.7 instead of 3.9:
- autogluon

## Set up

From this directory `./dev`.

```
cp /terraform/terraform.tfvars.template terraform/terraform.tfvars
```

Refresh the Riot Developer API key, only valid for 24 hours.

Edit the values with `vim` or `nano` with your tenancy, compartment, ssh public key and Riot API key:
```
vim terraform/terraform.tfvars
```

## Deploy

```
./start.sh
```

The output will be an `ssh` command to connect with the machine.

> Re-run the `start.sh` in case of failure

## Test

After ssh into the machine, run the check app.

```
python3 src/check.py
```

All checks should indicate `OK`. If any `FAIL`, review the setup and make sure `terraform.tfvars` are valid.

### Destroy

```
./stop.sh
```
