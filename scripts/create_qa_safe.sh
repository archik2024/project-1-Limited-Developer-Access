#!/bin/bash
# Скрипт для создания группы и пользователя QA в OCI с добавлением пользователя в группу
# Использует переменные из ~/.secrets/oci_ids.env

# Загружаем переменные окружения
source ~/.secrets/oci_ids.env

# Параметры группы
QA_GROUP_NAME="QA"
QA_GROUP_DESCRIPTION="QA team (testers)"

# Параметры пользователя
QA_USER_NAME="qa-user"
QA_USER_DESCRIPTION="QA engineer with limited Object Storage access"

echo "Создаём группу $QA_GROUP_NAME..."
GROUP_OCID=$(oci iam group create \
  --compartment-id "$TENANCY_OCID" \
  --name "$QA_GROUP_NAME" \
  --description "$QA_GROUP_DESCRIPTION" \
  --query "data.id" --raw-output)

echo "Группа $QA_GROUP_NAME создана: $GROUP_OCID"

echo "Создаём пользователя $QA_USER_NAME..."
USER_OCID=$(oci iam user create \
  --compartment-id "$TENANCY_OCID" \
  --name "$QA_USER_NAME" \
  --description "$QA_USER_DESCRIPTION" \
  --email "$QA_USER_EMAIL" \
  --query "data.id" --raw-output)

echo "Пользователь $QA_USER_NAME создан: $USER_OCID"

echo "Добавляем пользователя в группу..."
oci iam group add-user \
  --group-id "$GROUP_OCID" \
  --user-id "$USER_OCID"

echo "Пользователь $QA_USER_NAME добавлен в группу $QA_GROUP_NAME."
