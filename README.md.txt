# OCI IAM Task — Limited Developer Access to Object Storage

## 📌 Objective

Grant a developer access to a specific bucket in Oracle Cloud Infrastructure (OCI) Object Storage, with **no access to other resources**. The developer should be able to **upload/download objects** in this bucket only.

---

## 🧱 Resources

| Resource Type | Name               | Notes                         |
|---------------|--------------------|-------------------------------|
| Compartment   | `project-a`        | Target compartment            |
| Bucket        | `my-dev-logs`      | Object storage bucket         |
| Group         | `devs`             | IAM group for developers      |
| User          | `dev-user-01`      | IAM user account              |
| Policy        | `dev-access-policy`| IAM policy for access control |

---

## 🧭 Plan of Action

1. ✅ Create IAM group `devs`
2. ✅ Create IAM user `dev-user-01`
3. ✅ Add the user to the group
4. ✅ Generate API key for the user (for CLI access)
5. ✅ Create IAM policy:
   ```hcl
   allow group devs to manage objects in compartment project-a where target.bucket.name='my-dev-logs'
