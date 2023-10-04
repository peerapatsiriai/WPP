import frappe
from itertools import groupby


Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

@frappe.whitelist(allow_guest=True)
def allproducts():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """
                    SELECT cat.category_name,pro.product_id, product_name, img.image_file_name ,product_price,product_description, product_count, product_status, category_name, sup.sub_name FROM `tabproducts` AS pro
                    INNER JOIN `tabcategorys` AS cat
                    ON pro.product_category = cat.category_id
                    INNER JOIN `tabsuppliers` AS `sup`
                    ON pro.sub_id = sup.sub_id
                    INNER JOIN `tabproduct_image`As `img`
                    ON pro.product_id = img.product_id
                    WHERE pro.is_deleted = 0 AND product_status = 2 AND sup.sub_status != 0
                    ORDER BY pro.creation DESC
                """
        productList = frappe.db.sql(query, as_dict=1)
        
        if(len(productList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": productList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
       

@frappe.whitelist(allow_guest=True)
def productdetail(product_id):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        data_product_query = """ SELECT * FROM `tabproducts` WHERE product_id = '%s' """%(product_id)
        product_data_result = frappe.db.sql(data_product_query, as_dict=1)
        
        
        
        All_option_query = """ 
                            SELECT option_id,option_name 
                            FROM `tabproduct_options` 
                            WHERE product_id = '%s' 
                            """%(product_id)
        all_option = frappe.db.sql(All_option_query, as_dict=1)
        
        
        
        Option_query = """
                    SELECT option_name, value_name, val.value_order FROM `tabproducts` AS pro 
                    INNER JOIN `tabproduct_options` AS op
                    ON pro.product_id = op.product_id
                    INNER JOIN `tabproduct_option_values` AS val
                    ON op.option_id = val.option_id
                    WHERE pro.product_id = "%s"
                    ORDER BY value_order
                """ %(product_id)
        productList = frappe.db.sql(Option_query, as_dict=1)
        
        # Sort the data based on value_order
        sorted_data = sorted(productList, key=lambda x: x['value_order'])

        # Group the sorted data by value_order
        grouped_data = {}
        for key, group in groupby(sorted_data, key=lambda x: x['value_order']):
            grouped_data[f"Option{key}"] = list(group)
        
        if(len(productList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "AllOption":all_option, "data":product_data_result, "options": grouped_data }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
@frappe.whitelist(allow_guest=True)
def postnewproduct(sub_id, product_name, product_price, product_description, product_count, product_category):
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    parameterList = [sub_id, product_name, product_price, product_description, product_count, product_category]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    try:
        # Check if the username already exists
        existing_user = frappe.db.exists('products', {'product_name': product_name})
        if existing_user:
            return {"StatusCode": 409, "Message": "Suppliername already exists"}
        
        # Insert new account and get pk insert in tb member
        product_doc = frappe.get_doc({
            "doctype": "products",
            "sub_id": sub_id,
            "product_name": product_name,
            "product_price": product_price,
            "product_description": product_description,
            "product_count": product_count,
            "product_status": 1,
            "product_category": product_category,
        })
        product_doc.insert(ignore_permissions=True)
        
        # Update the account_id column with the value of the name
        product_doc.product_id = product_doc.name
        product_doc.save(ignore_permissions=True)
        
         
        return {"StatusCode": 201, "Message": "Register Success", "Primarykey": str(product_doc.product_id)}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def postnewproductv2(sub_id, product_name, product_category, product_description, product_brand, product_weight, product_license_number,product_county, product_size, product_amount, product_count, items, options):
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        # Insert Product Option in product DB
        product_doc = frappe.get_doc({
            "doctype": "products",
            "sub_id": sub_id,
            "product_name": product_name,
            "product_description": product_description,
            "product_count": product_count,
            "product_status": 1,
            "product_category": product_category,
            "product_brand": product_brand,
            "product_weight": product_weight,
            "product_county": product_county,
            "product_license_number": product_license_number,
            "product_amount": product_amount,
            "product_size": product_size,
        })
        product_doc.insert(ignore_permissions=True)
        
        # Update the account_id column with the value of the name
        product_doc.product_id = product_doc.name
        product_doc.save(ignore_permissions=True)
        
        column_name = []
        
        plire_doc = frappe.get_doc({
                "doctype": "product_options",
                "option_name": "Price",
                "product_id": product_doc.name
            })
        plire_doc.insert(ignore_permissions=True)
        plire_doc.option_id = plire_doc.name
        ###### 
        price_PK = plire_doc.name
        plire_doc.save(ignore_permissions=True)
        
        
        quantity_doc = frappe.get_doc({
                "doctype": "product_options",
                "option_name": "Quantity",
                "product_id": product_doc.name
            })
        quantity_doc.insert(ignore_permissions=True)
        quantity_doc.option_id = quantity_doc.name
        ###### 
        quantity_PK = quantity_doc.name
        quantity_doc.save(ignore_permissions=True)
        
        for option in options:
            option_doc = frappe.get_doc({
                "doctype": "product_options",
                "option_name": option["optionName"],
                "product_id": product_doc.name
            })
            option_doc.insert(ignore_permissions=True)
        
            # Update the account_id column with the value of the name
            option_doc.option_id = option_doc.name
            option_doc.save(ignore_permissions=True)
            # Add PK
            column_name.append(option_doc.name)

        while len(column_name) < 5:
            column_name.append("0")
            
        if column_name[0] != "0":
            for index,item in enumerate(items):
                
                option_value_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": column_name[0],
                    "value_name": item['optionGroupColumn1'],
                    "value_order": str(index+1)
                })
                option_value_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)
            
        if column_name[1] != "0":
            for index,item in enumerate(items):
                
                option_value_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": column_name[1],
                    "value_name": item['optionGroupColumn2'],
                    "value_order": str(index+1)
                })
                option_value_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)
                
        if column_name[2] != "0":
            for index,item in enumerate(items):
                print(str(index+1) +":" +column_name[2] +": " +item['optionGroupColumn3'])
                
                option_value_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": column_name[2],
                    "value_name": item['optionGroupColumn3'],
                    "value_order": str(index+1)
                })
                option_value_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)
                
        if column_name[3] != "0":
            for index,item in enumerate(items):
                print(str(index+1) +":" +column_name[3] +": " +item['optionGroupColumn4'])
                
                option_value_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": column_name[3],
                    "value_name": item['optionGroupColumn4'],
                    "value_order": str(index+1)
                })
                option_value_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)
                
        if column_name[4] != "0":
            for index,item in enumerate(items):
                print(str(index+1) +":" +column_name[4] +": " +item['optionGroupColumn5'])
                
                option_value_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": column_name[4],
                    "value_name": item['optionGroupColumn5'],
                    "value_order": str(index+1)
                })
                option_value_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)
                
        ## Insert Price
        for index,item in enumerate(items):
                
                option_value_price_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": price_PK,
                    "value_name": item['optionGroupPrice'],
                    "value_order": str(index+1)
                })
                option_value_price_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_price_doc.value_id = option_value_price_doc.name
                option_value_price_doc.save(ignore_permissions=True)
                
        ## Insert Quantity
        for index,item in enumerate(items):

                option_value_quantity_doc = frappe.get_doc({
                    "doctype": "product_option_values",
                    "option_id": quantity_PK,
                    "value_name": item['optionGroupQuantity'],
                    "value_order": str(index+1)
                })
                option_value_quantity_doc.insert(ignore_permissions=True)
            
                # Update the account_id column with the value of the name
                option_value_quantity_doc.value_id = option_value_quantity_doc.name
                option_value_quantity_doc.save(ignore_permissions=True)
        
        return {"StatusCode": 201, "Message": "Register Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def find_option_Detail(option_id):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [option_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        optiondata = """ 
                        SELECT * 
                        FROM `tabproduct_option_values` 
                        WHERE option_id = '%s' 
                    """%(option_id)
        optionResults = frappe.db.sql(optiondata, as_dict=1)
        
        if(len(productList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Result":optionResults }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}