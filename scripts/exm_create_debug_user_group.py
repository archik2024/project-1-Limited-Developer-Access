import os
from dotenv import load_dotenv
import oci

# Загружаем переменные окружения
load_dotenv()

# Конфигурация из ~/.oci/config (профиль по умолчанию)
config = oci.config.from_file("~/.oci/config", "DEFAULT")

# Инициализация клиентов
identity_client = oci.identity.IdentityClient(config)
tenancy_id = config["tenancy"]

# Переменные из .env
user_name = os.getenv("NEW_USER_NAME")
user_description = os.getenv("NEW_USER_DESCRIPTION")

group_name = os.getenv("NEW_GROUP_NAME")
group_description = os.getenv("NEW_GROUP_DESCRIPTION")

compartment_id = os.getenv("COMPARTMENT_OCID")
policy_name = os.getenv("POLICY_NAME")
policy_statements = os.getenv("POLICY_STATEMENTS", "").split(";")  # несколько через ;

# === Создание группы ===
create_group_response = identity_client.create_group(
    oci.identity.models.CreateGroupDetails(
        compartment_id=tenancy_id,
        name=group_name,
        description=group_description
    )
)
print(f"Создана группа: {create_group_response.data.name} ({create_group_response.data.id})")

# === Создание пользователя ===
create_user_response = identity_client.create_user(
    oci.identity.models.CreateUserDetails(
        compartment_id=tenancy_id,
        name=user_name,
        description=user_description
    )
)
print(f"Создан пользователь: {create_user_response.data.name} ({create_user_response.data.id})")

# === Добавляем пользователя в группу ===
add_user_response = identity_client.add_user_to_group(
    oci.identity.models.AddUserToGroupDetails(
        user_id=create_user_response.data.id,
        group_id=create_group_response.data.id
    )
)
print(f"Пользователь {user_name} добавлен в группу {group_name}")

# === Создаем политику ===
create_policy_response = identity_client.create_policy(
    oci.identity.models.CreatePolicyDetails(
        compartment_id=tenancy_id,
        name=policy_name,
        description="Policy created via script",
        statements=policy_statements
    )
)
print(f"Создана политика: {create_policy_response.data.name}")