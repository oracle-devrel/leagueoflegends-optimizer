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


## AJSON export/import

Create Bucket.

```
BEGIN
  DBMS_CLOUD.CREATE_CREDENTIAL(
    credential_name => 'LOL_BUCKET_CREDENTIALS',
    username => 'user1@example.com',
    password => 'password'
  );
END;
/
```

Match:
```
BEGIN
  DBMS_CLOUD.EXPORT_DATA(
    credential_name => 'LOL_BUCKET_CREDENTIALS',
    file_uri_list   => 'https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/namespace-string/b/lolbackup/o/match_export',
    query           => 'SELECT * FROM match',
    format          => JSON_OBJECT('type' value 'csv', 'delimiter' value '|', 'compression' value 'gzip'));
END;
/
```

Match Detail:
```
BEGIN
  DBMS_CLOUD.EXPORT_DATA(
    credential_name => 'LOL_BUCKET_CREDENTIALS',
    file_uri_list   => 'https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/namespace-string/b/lolbackup/o/match_detail_export',
    query           => 'SELECT * FROM match_detail',
    format          => JSON_OBJECT('type' value 'csv', 'delimiter' value '|', 'compression' value 'gzip'));
END;
/
```

Summoner:
```
BEGIN
  DBMS_CLOUD.EXPORT_DATA(
    credential_name => 'LOL_BUCKET_CREDENTIALS',
    file_uri_list   => 'https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/namespace-string/b/lolbackup/o/summoner_export',
    query           => 'SELECT * FROM summoner',
    format          => JSON_OBJECT('type' value 'csv', 'delimiter' value '|', 'compression' value 'gzip'));
END;
/
```

Predictor Live Client:
```
BEGIN
  DBMS_CLOUD.EXPORT_DATA(
    credential_name => 'LOL_BUCKET_CREDENTIALS',
    file_uri_list   => 'https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/namespace-string/b/lolbackup/o/predictor_liveclient_export',
    query           => 'SELECT * FROM predictor_liveclient',
    format          => JSON_OBJECT('type' value 'csv', 'delimiter' value '|', 'compression' value 'gzip'));
END;
/
```

> Update Credentials?
> ```
> BEGIN
>   DBMS_CLOUD.UPDATE_CREDENTIAL(
>      credential_name => 'LOL_BUCKET_CREDENTIALS',
>      attribute => 'PASSWORD',
>      value => '3UN-Ot2it$:Ib>cP!6YF'); 
> END;
> /
> ```