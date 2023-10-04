import frappe


Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# GET http://111.223.38.19/api/method/frappe.API.MasterData.academic.getAllAcademics
@frappe.whitelist(allow_guest=True)
def getAllAcademics():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """
                    SELECT * FROM `tabacademic_types` AS `act` 
                    INNER JOIN `tabacademics` AS `ac` 
                    ON act.name = ac.academic_type_ac_type_id
                    WHERE ac.is_deleted = 0
                    ORDER BY ac.creation DESC
                """
        academicsList = frappe.db.sql(query, as_dict=1)
        
        if(len(academicsList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": academicsList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.academic.insertacademic
@frappe.whitelist(allow_guest=True)
def insertacademic(ac_name_th, ac_name_en, ac_campus, ac_address, ac_tel, academic_type_ac_type_id):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ac_name_th, ac_name_en, ac_campus, ac_address, ac_tel, academic_type_ac_type_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "academics",
            "ac_id": "",  
            "ac_name_th": ac_name_th,
            "ac_name_en": ac_name_en,
            "ac_campus": ac_campus,
            "ac_address": ac_address,
            "ac_tel": ac_tel,
            "academic_type_ac_type_id": academic_type_ac_type_id
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.ac_id = doc.name
        doc.save(ignore_permissions=True)       
        
        return { "statusCode": 201, "message": "Insert Success", "Primarykey":str(doc.name) }


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.academic.editacademic
@frappe.whitelist(allow_guest=True)
def editacademic(ac_id, ac_name_th, ac_name_en, ac_campus, ac_address, ac_tel, academic_type_ac_type_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ac_id, ac_name_th, ac_name_en, ac_campus, ac_address, ac_tel, academic_type_ac_type_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    
    try:
        
        query = """ 
                    UPDATE `tabacademics`
                    SET ac_name_th = "%s", ac_name_en = "%s",ac_campus = "%s", ac_address = "%s", ac_tel = "%s",
                    academic_type_ac_type_id = "%s", modified = NOW()
                    WHERE ac_id = "%s" 
                """ %(ac_name_th, ac_name_en, ac_campus, ac_address, ac_tel, academic_type_ac_type_id,ac_id)
                
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 200, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}