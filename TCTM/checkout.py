import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def check_out_detail(member_id):
    
    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # get all data of one member
        query = """ 
                    SELECT user_address, user_tel, user_email
                    FROM `tabmembers` 
                    WHERE member_id = %s
                """

        member_data_detail = frappe.db.sql(query, [member_id],as_dict=1)

        if len(member_data_detail) == 0:
            write_log("System call api checkout detail but not found at member id: " + member_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("System call api checkout detail at member id " + member_id)
            return {"stausCode": "200", "message": "OK", "Data": member_data_detail}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        write_log("System call api checkout detail but error " + str(e))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
@frappe.whitelist(allow_guest=True)
def market_number_bank(sub_id, invoice_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # get all data of one market
        query_bank_data = """ 
                    SELECT sub_name,sub_bank_name,sub_bank_number, sub_book_bank_name, sub_pay_name, sub_pay_number
                    FROM `tabsuppliers`
                    WHERE sub_id = %s
                """
                
        # get all data of invoice
        query_invoice_data = """ 
                    SELECT product_name, product_amount, product_brand, product_county, price_total
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabproducts` AS `pro`
                    ON pro.name = in.product_id
                    WHERE invoice_id = %s
                """

        member_data_detail = frappe.db.sql(query_bank_data, [sub_id],as_dict=1)
        invoice_data = frappe.db.sql(query_invoice_data, [invoice_id],as_dict=1)

        if len(member_data_detail) == 0:
            write_log("System call api market number bank at market id " + sub_id + " and invoice id " + invoice_id + " but not found bank data")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("System call api market number bank at market id " + sub_id + " and invoice id " + invoice_id)
            return {"stausCode": "200", "message": "OK", "Data": member_data_detail, "Invoice": invoice_data}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        write_log("System call api market number bank but error " + str(e))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

