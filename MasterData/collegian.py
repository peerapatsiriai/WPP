import frappe

###########################################################################################################################
################################################### Collegian #############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.collegian.getAllcollegians
@frappe.whitelist(allow_guest=True)
def getAllcollegians():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query1 = """ 
                    SELECT * FROM `tabfaculty_institutes` AS `fac` 
                    INNER JOIN `tabcollegians` AS `co` 
                    ON fac.fi_id = co.faculty_institutes_fi_id 
                    
                    INNER JOIN `tabcurriculums` AS `cu`
                    on co.curriculums_cur_id = cu.cur_id
                    
                    INNER JOIN `tabacademics` AS `ac`
                    on ac.ac_id = fac.academics_ac_id
                    WHERE co.is_deleted = 0
                    ORDER BY co.creation DESC
                 """ 
        # query2 = """ 
        #             SELECT ac.ac_id FROM `tabcollegians` AS `co` 
        #             INNER JOIN `tabfaculty_institutes` AS `fac` 
        #             ON fac.fi_id = co.faculty_institutes_fi_id 
                    
        #             INNER JOIN `tabacademics` AS `ac`
        #             on ac.ac_id = fac.academics_ac_id
                    
        #             INNER JOIN `tabcurriculums` AS `cur`
        #             ON co.curriculums_cur_id = cur.cur_id
                    
        #             WHERE co.is_deleted = 0
        #             ORDER BY co.creation DESC
        #         """
        collegiansList = frappe.db.sql(query1, as_dict=1)
        
        # academicsid = frappe.db.sql(query2, as_dict=1)
        
        if(len(collegiansList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": collegiansList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.collegian.insertcollegian
@frappe.whitelist(allow_guest=True)
def insertcollegian(co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id, curriculums_cur_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id, curriculums_cur_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "collegians",
            "co_id": "IN-",  
            "co_code": co_code,
            "co_fname_th": co_fname_th,
            "co_lname_th": co_lname_th,
            "co_fname_en": co_fname_en,
            "co_lname_en": co_lname_en,
            "co_email": co_email,
            "co_tel": co_tel,
            "faculty_institutes_fi_id": faculty_institutes_fi_id,
            "curriculums_cur_id": curriculums_cur_id
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.co_id = doc.name
        doc.save(ignore_permissions=True)
        
        # # get Date and Milliseconds to Primarykey
        # today = datetime.datetime.now()
        # formatted_datetime = today.strftime("%d%m%Y%f") 
        # primarykey = int(formatted_datetime)     
        
        # query = """
        #            INSERT INTO `tabcollegians` 
        #            (name, creation, modified, modified_by, owner, docstatus, idx, co_id, 
        #            co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id) 
        #            VALUES (%d, NOW(), NOW(), 'Administrator', 'Administrator', 0, 0, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
        #         """ % (
        #     primarykey, primarykey, co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id
        #             )
                
        # frappe.db.sql(query, as_dict=1)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.collegian.editcollegian
@frappe.whitelist(allow_guest=True)
def editcollegian(co_id, co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [co_id, co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_email, co_tel, faculty_institutes_fi_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabcollegians`
                    SET co_code = "%s", co_fname_th = "%s", co_lname_th = "%s", co_fname_en = "%s", co_lname_en = "%s", co_tel = "%s",
                    faculty_institutes_fi_id = "%s", modified = NOW()
                    WHERE co_id = "%s" 
                """ % (
                    co_code, co_fname_th, co_lname_th, co_fname_en, co_lname_en, co_tel, faculty_institutes_fi_id, co_id
                    )
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

### GEt Collegian PK 

# ----------------------- #
# Customs API 
# ----------------------- #
    
# GET http://111.223.38.19/api/method/frappe.API.MasterData.collegian.getAllCurriculumandFacultyinoneacademic
@frappe.whitelist(allow_guest=True)
def getAllCurriculumandFacultyinoneacademic(ac_id):  
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [ac_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        Academic_id = ac_id
        query1 = """
                    SELECT fi_id, fi_name_th, fi_name_en FROM `tabfaculty_institutes`
                    WHERE academics_ac_id = %s   
                """

        facultyList = frappe.db.sql(query1, (Academic_id),as_dict=True)
    
        query2 = """
                    SELECT cur.cur_id, cur.cur_name_th, cur.cur_name_en, cur.cur_shot_name_th, cur.cur_shot_name_en
                    FROM `tabcurriculums` AS `cur` 
                    INNER JOIN `tabfaculty_institutes` AS `fi` ON cur.faculty_institutes_fi_id = fi.fi_id
                    INNER JOIN `tabacademics` AS `ac` ON ac.ac_id = fi.academics_ac_id
                    WHERE ac.ac_id = %s
                """  
        curriculumsList = frappe.db.sql(query2, (Academic_id),as_dict=True)
        return { "statusCode": 202, "message": "Get Data Success","Academic":Academic_id ,"FacultyList":facultyList, "CurriculumsList":curriculumsList }
   
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}