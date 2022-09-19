#!/bin/bash

start_time=$(date +%s)

banner()
{
  echo "+------------------------------------------+"
  printf "| %-40s |\n" "`date`"
  echo "|                                          |"
  printf "|`tput bold` %-40s `tput sgr0`|\n" "$@"
  echo "+------------------------------------------+"
}

checkpoint()
{
  if [ $? -ne 0 ]; then
    exit $?
  fi
}

if [ -z "$BASE_DIR" ]
then
  export BASE_DIR=$(pwd)
fi

banner "Terraform Init"
cd $BASE_DIR/terraform
terraform init
checkpoint

banner "Terraform Apply"
terraform apply -auto-approve
checkpoint

sleep 2

banner "Ansible Provisioning"
export ANSIBLE_HOST_KEY_CHECKING=False
ansible-playbook -i generated/app.ini ../ansible/server/server.yaml
checkpoint

banner "Output"
terraform output
checkpoint

cd $BASE_DIR

end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
echo "Time: $elapsed sec"