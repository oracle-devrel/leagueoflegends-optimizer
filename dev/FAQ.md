# FAQ Automation

## Lab 2, Task 3: Start Deployment

The output of `./start.sh` is not the expected and in red says:
```
oci_core_instance.compute[0]: Creating...
╷
│ Error: 500-InternalError, Out of host capacity.
│ Suggestion: The service for this resource encountered an error. Please contact support for help with service: Core Instance
│ Documentation: https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance 
│ API Reference: https://docs.oracle.com/iaas/api/#/en/iaas/20160918/Instance/LaunchInstance
```

### Solution:
```
cd terraform && terraform output compute_available_shapes && cd ..
```

The results will be like this, don't worry if they are not exactly the same:
```
[
  "VM.Standard.E4.Flex",
  "VM.Standard.E3.Flex",
  "VM.Standard.A1.Flex",
  "VM.Standard3.Flex",
]
```

By default, we use `VM.Standard.E4.Flex`. So, pick another one and put a new variable on the `terraform.tfvars`. Just like this:
```
instance_shape              = "VM.Standard.E3.Flex"
```

Run again the start script again
```
./start.sh
```

---

## Lab 2, Task 3: Start Deploying

```
+------------------------------------------+
| Thu Sep  8 13:17:41 UTC 2022             |
|                                          |
| Ansible Provisioning                     |
+------------------------------------------+

PLAY [Provision Python Flask App] ******************************************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] *****************************************************************************************************************************************************************************************************************************************************
fatal: [node1]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: FIPS mode initialized\r\nssh: connect to host 141.148.242.12 port 22: Connection refused", "unreachable": true}

PLAY RECAP *****************************************************************************************************************************************************************************************************************************************************************
node1                      : ok=0    changed=0    unreachable=1    failed=0    skipped=0    rescued=0    ignored=0
```

### Solution

Run again the start script again
```
./start.sh
```