import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def register(
    username,
    password,
    user_email,
    user_first_name,
    user_last_name,
    user_company,
    user_address,
    user_tel,
    user_birthday):

    if Api_Maintenance or Server_Maintenance:
        return {
            "StatusCode": "503",
            "Message": "This API is currently under maintenance.",
        }

    parameterList = [
        username,
        password,
        user_email,
        user_first_name,
        user_last_name,
        user_company,
        user_address,
        user_tel,
        user_birthday,
    ]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:
        # Check if the username already exists
        existing_user = frappe.db.exists("accounts", {"account_username": username})
        if existing_user:
            return {"StatusCode": 409, "Message": "Username already exists"}

        # Insert new account and get pk insert in tb member
        account_doc = frappe.get_doc(
            {
                "doctype": "accounts",
                "account_username": username,
                "account_password": password,
                "account_status": 1, # status 1 is wati for approve
            }
        )
        account_doc.insert(ignore_permissions=True)

        # Update the account_id column with the value of the name
        account_doc.account_id = account_doc.name
        account_doc.save(ignore_permissions=True)

        # Insert the member and the generated primary key
        member_doc = frappe.get_doc(
            {
                "doctype": "members",
                "account_id": account_doc.name,
                "user_first_name": user_first_name,
                "user_last_name": user_last_name,
                "user_company": user_company,
                "user_status": 1, # status 1 is wait for approve
                "user_address": user_address,
                "user_tel": user_tel,
                "user_birthday": user_birthday,
                "user_email": user_email,
                "user_role": "USER",
            }
        )

        member_doc.insert(ignore_permissions=True)

        # Update the member_id column with the value of the name
        member_doc.member_id = member_doc.name
        member_doc.save(ignore_permissions=True)

        write_log("Account "+ account_doc.name + " " + user_first_name + " " + user_last_name + " Registered")
        return {
            "StatusCode": 201,
            "Message": "Insert Success",
            "Primarykey": str(member_doc.member_id),
        }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Account "+ account_doc.name + " " + user_first_name + " " + user_last_name + " Registration Failed")
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def registerMarket(
    sub_bank_number,
    member_id,
    sub_tel,
    sub_email,
    sub_image,
    sub_name,
    sub_description,
    sub_address,
    sub_address_shop,
    sub_address_claim,
    
    sub_bank_name,
    sub_book_bank_name,
    sub_pay_name,
    sub_pay_number):

    if Api_Maintenance or Server_Maintenance:
        return {
            "StatusCode": "503",
            "Message": "This API is currently under maintenance.",
        }

    parameterList = [
        sub_bank_number,
        sub_tel,
        sub_email,
        sub_name,
        sub_description,
        sub_address,
        sub_address_shop,
        sub_address_claim,
        member_id,
        sub_bank_name,
        sub_book_bank_name,
        sub_pay_name,
        sub_pay_number
    ]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:
        # Check if the marketname already exists
        existing_user = frappe.db.exists("suppliers", {"sub_name": sub_name})
        if existing_user:
            return {"StatusCode": 409, "Message": "Suppliername already exists"}

        # Insert new market and get pk insert in tb market
        suppliers_doc = frappe.get_doc(
            {
                "doctype": "suppliers",
                "sub_bank_number": sub_bank_number,
                "sub_tel": sub_tel,
                "sub_email": sub_email,
                "sub_name": sub_name,
                "sub_image": sub_image,
                "sub_description": sub_description,
                "sub_address": sub_address,
                "sub_address_shop": sub_address_shop,
                "sub_address_claim": sub_address_claim,
                "sub_status": 1, # status 1 is wait for approve
                "sub_bank_name": sub_bank_name,
                "sub_book_bank_name": sub_book_bank_name,
                "sub_pay_name": sub_pay_name,
                "sub_pay_number": sub_pay_number
            }
        )
        suppliers_doc.insert(ignore_permissions=True)

        # Update the market_id column with the value of the name
        suppliers_doc.sub_id = suppliers_doc.name
        suppliers_doc.save(ignore_permissions=True)

        # Get Doctype at member_id
        member_doc = frappe.get_doc("members", member_id)

        # Update member status from 1 to 2
        # Update member supplier with market PK
        member_doc.sub_id = suppliers_doc.sub_id
        member_doc.user_status = 2 # status 2 is this user have market
        member_doc.save(ignore_permissions=True)

        write_log("Market "+ suppliers_doc.sub_name + " of member " + member_doc.user_first_name + " " + member_doc.user_last_name + " Registered")
        return {
            "StatusCode": 201,
            "Message": "Register Success",
            "Primarykey": str(member_doc.sub_id),
        }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Account "+ account_doc.name + " " + user_first_name + " " + user_last_name + " Registered")
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
