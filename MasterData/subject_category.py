import frappe

###########################################################################################################################
###############################################  Subject category  ########################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# GET http://111.223.38.19/api/method/frappe.API.MasterData.subject_category.getAllsubject_category
@frappe.whitelist(allow_guest=True)
def getAllsubject_category():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabsubject_category` AS `subc`
                    WHERE subc.is_deleted = 0
                    ORDER BY subc.creation DESC
                """
        subjectCategoryList = frappe.db.sql(query, as_dict=1)
        
        if(len(subjectCategoryList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": subjectCategoryList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.subject_category.insertsubject_category
@frappe.whitelist(allow_guest=True)
def insertsubject_category(subject_category_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_category_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "subject_category",
            "subject_type_id": "SJC-",  
            "subject_category_name":subject_category_name,  
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.subject_category_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject_category.editsubject_category
@frappe.whitelist(allow_guest=True)
def editsubject_category(subject_category_id, subject_category_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_category_name ,subject_category_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabsubject_category`
                    SET subject_category_name = "%s", modified = NOW()
                    WHERE subject_category_id = "%s" 
                """ % (subject_category_name, subject_category_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}