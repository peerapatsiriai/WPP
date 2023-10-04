import frappe

###########################################################################################################################
################################################### Facultys ##############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# GET http://111.223.38.19/api/method/frappe.API.MasterData.faculty.getAllfacultys
@frappe.whitelist(allow_guest=True)
def getAllfacultys():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """
                    SELECT * FROM `tabacademics` AS `ac` 
                    INNER JOIN `tabfaculty_institutes` AS `fi` 
                    ON ac.name = fi.academics_ac_id
                    WHERE fi.is_deleted = 0 
                    ORDER BY fi.creation DESC
                """
        academics = frappe.db.sql(query, as_dict=1)
        
        if(len(academics) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": academics }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    

# POST http://111.223.38.19/api/method/frappe.API.MasterData.faculty.insertfaculty
@frappe.whitelist(allow_guest=True)
def insertfaculty(fi_name_th, fi_name_en, academics_ac_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
        
    parameterList = [fi_name_th, fi_name_en, academics_ac_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "faculty_institutes",
            "fi_id": "",  
            "fi_name_th": fi_name_th,
            "fi_name_en": fi_name_en,
            "academics_ac_id": academics_ac_id
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.fi_id = doc.name
        doc.save(ignore_permissions=True)       
       
        
        return { "statusCode": 201, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}


# PUT http://111.223.38.19/api/method/frappe.API.MasterData.faculty.editfaculty
@frappe.whitelist(allow_guest=True)
def editfaculty(fi_id, fi_name_th, fi_name_en, academics_ac_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [fi_id, fi_name_th, fi_name_en, academics_ac_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query = """ 
                    UPDATE `tabfaculty_institutes`
                    SET fi_name_th = "%s", fi_name_en = "%s", academics_ac_id = "%s", modified = NOW()
                    WHERE fi_id = "%s" 
                """ %(fi_name_th, fi_name_en, academics_ac_id, fi_id)
                
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 200, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}