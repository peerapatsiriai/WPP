import frappe

###########################################################################################################################
################################################### Instructors ############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.instructor.getAllinstructors
@frappe.whitelist(allow_guest=True)
def getAllinstructors():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabfaculty_institutes` AS `fac` 
                    INNER JOIN `tabinstructors` AS `in` 
                    ON fac.name = in.faculty_institutes_fi_id 
                    WHERE in.is_deleted = 0
                    ORDER BY in.creation DESC
                """
        instructorList = frappe.db.sql(query, as_dict=1)
        
        if(len(instructorList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": instructorList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.instructor.insertinstructors
@frappe.whitelist(allow_guest=True)
def insertinstructors(ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "instructors",
            "ist_id": "IN-",  
            "ist_fname_th": ist_fname_th,
            "ist_lname_th": ist_lname_th,
            "ist_fname_en": ist_fname_en,
            "ist_lname_en": ist_lname_en,
            "ist_email": ist_email,
            "ist_tel": ist_tel,
            "faculty_institutes_fi_id": faculty_institutes_fi_id,
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.ist_id = doc.name
        doc.save(ignore_permissions=True)
        
        # get Date and Milliseconds to Primarykey
        # today = datetime.datetime.now()
        # formatted_datetime = today.strftime("%d%m%Y%f") 
        # primarykey = int(formatted_datetime)     
        
        # query = """
        #            INSERT INTO `tabinstructors` 
        #            (name, creation, modified, modified_by, owner, docstatus, idx, ist_id,
        #            ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id) 
        #            VALUES (%d, NOW(), NOW(),
        #            'Administrator', 'Administrator', 0, 0, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s')
        #         """ % (primarykey, primarykey, ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id)
                
        # frappe.db.sql(query, as_dict=1)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.instructor.editinstructor
@frappe.whitelist(allow_guest=True)
def editinstructor(ist_id, ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ist_id, ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabinstructors`
                    SET ist_fname_th = "%s", ist_lname_th = "%s", ist_fname_en = "%s", ist_lname_en = "%s", ist_email = "%s", ist_tel = "%s",
                    faculty_institutes_fi_id = "%s", modified = NOW()
                    WHERE ist_id = "%s" 
                """ % (ist_fname_th, ist_lname_th, ist_fname_en, ist_lname_en, ist_email, ist_tel, faculty_institutes_fi_id,ist_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}