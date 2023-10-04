import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def allproductinmarket(member_id):

    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        query1 = """
                    SELECT sub.sub_id,sub_name,sub_status, sub_email, sub_address FROM `tabmembers` AS `mem`
                    INNER JOIN `tabsuppliers` AS `sub`
                    ON mem.sub_id = sub.sub_id
                    WHERE member_id = %s
                """
        # Status 4 is product not selling
        query2 = """
                    SELECT product_id, product_name, product_description, product_count, product_status, category_id,category_name FROM `tabproducts` AS `pro`
                    INNER JOIN `tabcategorys` AS `cat`
                    ON pro.product_category = cat.category_id
                    WHERE sub_id =  %s AND product_status > 0 AND is_deleted = 0 
                    ORDER BY pro.creation DESC
                """ 
        query3 = """
                    SELECT COUNT(name) FROM `tabproducts` AS `pro`
                    WHERE sub_id = %s AND is_deleted = 0
                    ORDER BY pro.creation DESC
                """
                
        # Get member_id for fild sub_id
        result = frappe.db.sql(query1, (member_id),as_dict=1)
        sup_id = result[0].sub_id # sub_id is PK of market
        
        queue = frappe.db.sql(query2, (sup_id), as_dict=1) # fild all product in market
        count = frappe.db.sql(query3, (sup_id), as_dict=1) # count all product in market

        return {
            "stausCode": "200",
            "message": "OK",
            "Data": queue,
            "ProductCount": count,
            "MarketData": result,
        }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
