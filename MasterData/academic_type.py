import frappe

###########################################################################################################################
################################################## Academic Type ##########################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# GET http://111.223.38.19/api/method/frappe.API.MasterData.academic_type.getallacademictype
@frappe.whitelist(allow_guest=True)
def getallacademictype():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
            
        query = """ 
                    SELECT * 
                    FROM `tabacademic_types` 
                    WHERE is_deleted = "0" 
                    ORDER BY creation DESC
                """
                
        academicsTypeList = frappe.db.sql(query, as_dict=1)
        
        if(len(academicsTypeList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": academicsTypeList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# POST http://111.223.38.19/api/method/frappe.API.MasterData.academic_type.insertacademictype
@frappe.whitelist(allow_guest=True)
def insertacademictype(ac_type_name_th, ac_type_name_en, ac_area):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
        
    parameterList = [ac_type_name_th, ac_type_name_en, ac_area]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "academic_types",
            "ac_type_id": "ACT-",  
            "ac_type_name_th": ac_type_name_th,
            "ac_type_name_en": ac_type_name_en,
            "ac_area": ac_area,
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.ac_type_id = doc.name
        doc.save(ignore_permissions=True)                     
        
        return { "statusCode": 201, "message": "Insert Success", "Primarykey":str(doc.name) }


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"StatusCode": 500, "Message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.academic_type.editacademictype
@frappe.whitelist(allow_guest=True)
def editacademictype(ac_type_id,ac_type_name_th, ac_type_name_en, ac_area):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ac_type_id,ac_type_name_th, ac_type_name_en, ac_area]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query = """ 
                    UPDATE `tabacademic_types`
                    SET ac_type_name_th = "%s", ac_type_name_en = "%s", ac_area = "%s", modified = NOW()
                    WHERE ac_type_id = "%s" 
                """ %(ac_type_name_th, ac_type_name_en, ac_area, ac_type_id)
                
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 200, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}