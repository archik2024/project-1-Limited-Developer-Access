# scripts/create_debug_user_group.py
from pathlib import Path
import os
import oci
from dotenv import load_dotenv

# --- .env ---
dotenv_path = Path.home() / ".secrets" / ".env"
load_dotenv(dotenv_path)

user_name   = os.getenv("DEBUG_USER_NAME")
user_email  = os.getenv("DEBUG_USER_EMAIL")
group_name  = os.getenv("DEBUG_GROUP_NAME")
tenancy_env = os.getenv("TENANCY_OCID")  # ВАЖНО: для IAM операций

if not user_name or not user_email or not group_name:
    raise ValueError("В .env должны быть DEBUG_USER_NAME, DEBUG_USER_EMAIL, DEBUG_GROUP_NAME")

# --- OCI config (админская основа) ---
config = oci.config.from_file("~/.oci/config", "DEFAULT")
identity = oci.identity.IdentityClient(config)

# Выбираем tenancy для IAM-операций: сначала из .env, иначе из конфига
tenancy_id = tenancy_env or config["tenancy"]

# Если оба заданы и не совпадают — предупредим (используем тот, что в конфиге клиента)
if tenancy_env and tenancy_env != config["tenancy"]:
    print(f"⚠️ Предупреждение: TENANCY_OCID из .env ({tenancy_env}) не совпадает с tenancy в ~/.oci/config ({config['tenancy']}).")
    print("   Для согласованности операций будет использован tenancy из ~/.oci/config.")
    tenancy_id = config["tenancy"]

def find_group_by_name(name: str):
    # Группы — на уровне tenancy
    groups = identity.list_groups(compartment_id=tenancy_id).data
    for g in groups:
        if g.name == name:
            return g
    return None

def find_user_by_name(name: str):
    # Пользователи — на уровне tenancy
    users = identity.list_users(compartment_id=tenancy_id).data
    for u in users:
        if u.name == name:
            return u
    return None

def ensure_group(name: str, description: str):
    existing = find_group_by_name(name)
    if existing:
        print(f"Группа уже существует: {existing.name}, OCID: {existing.id}")
        return existing
    details = oci.identity.models.CreateGroupDetails(
        name=name,
        description=description,
        compartment_id=tenancy_id,  # тут всегда TENANCY_OCID
    )
    grp = identity.create_group(details).data
    print(f"Группа создана: {grp.name}, OCID: {grp.id}")
    return grp

def ensure_user(name: str, email: str, description: str):
    existing = find_user_by_name(name)
    if existing:
        print(f"Пользователь уже существует: {existing.name}, OCID: {existing.id}")
        return existing
    details = oci.identity.models.CreateUserDetails(
        name=name,
        description=description,
        email=email,
        compartment_id=tenancy_id,  # тут всегда TENANCY_OCID
    )
    usr = identity.create_user(details).data
    print(f"Пользователь создан: {usr.name}, OCID: {usr.id}")
    return usr

def ensure_membership(user_id: str, group_id: str):
    # Проверим, есть ли уже membership
    memberships = identity.list_user_group_memberships(
        compartment_id=tenancy_id, user_id=user_id, group_id=group_id
    ).data
    if memberships:
        print(f"Пользователь уже в группе, membership ID: {memberships[0].id}")
        return memberships[0]
    add = oci.identity.models.AddUserToGroupDetails(user_id=user_id, group_id=group_id)
    m = identity.add_user_to_group(add).data
    print(f"Пользователь добавлен в группу, membership ID: {m.id}")
    return m

# --- Выполнение ---
group = ensure_group(group_name, "Debuggers group")
user  = ensure_user(user_name, user_email, "Debug automation user")
ensure_membership(user.id, group.id)