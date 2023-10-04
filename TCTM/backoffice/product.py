import frappe
from ..write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# products queue
@frappe.whitelist(allow_guest=True)
def allproduct():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Get all product in system not condition
        query = """
                    SELECT pro.product_id, pro.sub_id, pro.product_name,pro.product_price,pro.product_status,pro.product_category,sup.sub_name, cat.category_name
                    FROM tabproducts AS pro
                    INNER JOIN tabsuppliers AS sup
                    ON pro.sub_id = sup.sub_id
                    INNER JOIN tabcategorys AS cat
                    ON pro.product_category = cat.category_id
                    ORDER BY pro.creation DESC;
                """
        queue = frappe.db.sql(query, as_dict=1)
        
        if(len(queue) == 0):
            
            write_log("Admin call api get all product but not found any data.")
            
            return { "stausCode":"404", "message":"Not Found" }
        else:
            write_log("Admin call api get all product")
            return { "stausCode":"200", "message":"OK", "Data": queue }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("Admin call api allproduct but errer {}".format(str(e)))
        
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# Ban product
@frappe.whitelist(allow_guest=True)
def ban(product_id):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}

    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        # Update product Status at product_id. status 0 is this product has baned in system
        query = """UPDATE `tabproducts` SET product_status = 0 WHERE product_id = '%s'""" % (product_id)
        frappe.db.sql(query)

        # Commit the transaction
        frappe.db.commit()

        write_log("Admin ban product {}".format(product_id))
        
        return {"statusCode": 200, "message": "Baned"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("Admin ban product but errer {}".format(str(e)))
        
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# Unban product
@frappe.whitelist(allow_guest=True)
def unban(product_id):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}

    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        #  Update product Status at product_id. status 1 is product wait for approve
        query = """UPDATE `tabproducts` SET product_status = 1 WHERE product_id = '%s'""" % (product_id)
        frappe.db.sql(query)

        # Commit the transaction
        frappe.db.commit()

        # query = """SELECT * FROM tabproducts WHERE name = '%s' """ % (product_id)
        # data = frappe.db.sql(query, as_dict=True)
        write_log("Admin unban product {}".format(product_id))
        return {"statusCode": 200, "message": "Un Baned"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        write_log("Admin ban product but errer {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    

    
    
    
