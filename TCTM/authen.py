import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def login(username, password):

    parameterList = [username, password]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Find user in system
        query = """
                    SELECT *
                    FROM `tabaccounts` 
                    WHERE account_username = %s AND account_password = %s
                """

        accountResult = frappe.db.sql(query, (username, password), as_dict=1)

        # Check have user in system
        if len(accountResult) == 0:
            return { "StatusCode": "404", "Message": "Not found user or invalid password" }
        else:
            # Set value status
            account_id = accountResult[0].get("account_id")
            account_status = accountResult[0].get("account_status")

            if account_status == "0":
                return { "StatusCode": "200", "Message": "Banned", "AccountStatus": account_status }
            if account_status == "1":
                return { "StatusCode": "200", "Message": "Wait approve", "AccountStatus": account_status }
            
            # If account normal
            # pair data of user with account and ruturn user data
            query2 = """
                        SELECT mem.member_id, mem.user_first_name, mem.user_last_name, mem.user_email, mem.user_role, mem.user_status
                        FROM `tabmembers` AS mem
                        INNER JOIN `tabaccounts` AS ac ON mem.account_id = ac.account_id
                        WHERE mem.account_id = %s
                     """

            response = frappe.db.sql(query2, (account_id,), as_dict=1)
            
            write_log("Account "+ account_id + " " +response[0].user_first_name + " " + response[0].user_last_name + " Login in system")

            return {"StatusCode": "200", "Message": "OK", "Data": response}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Login but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
