import frappe
from itertools import groupby
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# display all product in system
@frappe.whitelist(allow_guest=True)
def allproducts():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all product in system condition is not deleted and product approved  and market approved
        query = """
                    SELECT
                        cat.category_name,
                        pro.product_id, 
                        product_name, 
                        img.image_file_name,
                        product_description, 
                        product_status, 
                        category_name, 
                        sup.sub_name,
                        MIN(CAST(opv.value_name AS DECIMAL(10))) AS min_price,
                        MAX(CAST(opv.value_name AS DECIMAL(10))) AS max_price
                    FROM
                        `tabproducts` AS pro
                    INNER JOIN
                        `tabcategorys` AS cat ON pro.product_category = cat.category_id
                    INNER JOIN
                        `tabsuppliers` AS sup ON pro.sub_id = sup.sub_id
                    INNER JOIN
                        `tabproduct_image` AS `img` ON pro.product_id = img.product_id
                    INNER JOIN
                        `tabproduct_options` AS `opn` ON opn.product_id = pro.product_id
                    INNER JOIN
                        `tabproduct_option_values` AS `opv` ON opv.option_id = opn.option_id
                    WHERE
                        pro.is_deleted = 0
                        AND product_status > 1
                        AND sup.sub_status != 0
                        AND opn.option_name = "Price"
                        AND pro.product_status != 4
                    GROUP BY
                        pro.product_id, opn.option_name
                    ORDER BY
                        pro.creation DESC;
                """
        productList = frappe.db.sql(query, as_dict=1)

        if len(productList) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": productList}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

# display all product in one market
@frappe.whitelist(allow_guest=True)
def allproducts_market(sup_id):

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all product in system condition is not deleted and product approved  and market approved
        query = """
                    SELECT
                        cat.category_name,
                        pro.product_id, 
                        product_name, 
                        img.image_file_name,
                        product_description, 
                        product_status, 
                        category_name, 
                        sup.sub_name,
                        MIN(CAST(opv.value_name AS DECIMAL(10))) AS min_price,
                        MAX(CAST(opv.value_name AS DECIMAL(10))) AS max_price
                    FROM
                        `tabproducts` AS pro
                    INNER JOIN
                        `tabcategorys` AS cat ON pro.product_category = cat.category_id
                    INNER JOIN
                        `tabsuppliers` AS sup ON pro.sub_id = sup.sub_id
                    INNER JOIN
                        `tabproduct_image` AS `img` ON pro.product_id = img.product_id
                    INNER JOIN
                        `tabproduct_options` AS `opn` ON opn.product_id = pro.product_id
                    INNER JOIN
                        `tabproduct_option_values` AS `opv` ON opv.option_id = opn.option_id
                    WHERE
                        pro.is_deleted = 0
                        AND pro.sub_id = %s
                        AND product_status > 1
                        AND sup.sub_status != 0
                        AND opn.option_name = "Price"
                    GROUP BY
                        pro.product_id, opn.option_name
                    ORDER BY
                        pro.creation DESC;
                """
        productList = frappe.db.sql(query, [sup_id],as_dict=1)

        if len(productList) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": productList}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
# post product detial of one product
@frappe.whitelist(allow_guest=True)
def productdetail(product_id):

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    try:
        
        # Get product data in product_id
        data_product_query = (
            """ SELECT * FROM `tabproducts` WHERE product_id = '%s' """ % (product_id)
        )
        product_data_result = frappe.db.sql(data_product_query, as_dict=1)
        
        # Find all product option name in product_id
        All_option_query = """ 
                            SELECT option_id,option_name 
                            FROM `tabproduct_options` 
                            WHERE product_id = '%s' 
                            """ % (product_id)
                            
        all_option = frappe.db.sql(All_option_query, as_dict=1)

        # Get all product option value in product_id
        Option_query = """
                    SELECT option_name, value_name, val.value_order FROM `tabproducts` AS pro 
                    INNER JOIN `tabproduct_options` AS op
                    ON pro.product_id = op.product_id
                    INNER JOIN `tabproduct_option_values` AS val
                    ON op.option_id = val.option_id
                    WHERE pro.product_id = "%s"
                    ORDER BY value_order
                """ % (product_id)
        productList = frappe.db.sql(Option_query, as_dict=1)

        # Sort the data based on value_order
        sorted_data = sorted(productList, key=lambda x: x["value_order"])

        # Group the sorted data by value_order
        grouped_data = {}
        for key, group in groupby(sorted_data, key=lambda x: x["value_order"]):
            grouped_data[f"Option{key}"] = list(group)

        if len(productList) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {
                "stausCode": "200",
                "message": "OK",
                "AllOption": all_option,
                "data": product_data_result,
                "options": grouped_data,
            }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }

# Not use this API
@frappe.whitelist(allow_guest=True)
def postnewproduct(
    sub_id,
    product_name,
    product_price,
    product_description,
    product_count,
    product_category):

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [
        sub_id,
        product_name,
        product_price,
        product_description,
        product_count,
        product_category,
    ]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:
        # Check if the username already exists
        existing_user = frappe.db.exists("products", {"product_name": product_name})
        if existing_user:
            return {"StatusCode": 409, "Message": "Suppliername already exists"}

        # Insert new product and get product PK
        product_doc = frappe.get_doc(
            {
                "doctype": "products",
                "sub_id": sub_id,
                "product_name": product_name,
                "product_price": product_price,
                "product_description": product_description,
                "product_count": product_count,
                "product_status": 1,
                "product_category": product_category,
            }
        )
        product_doc.insert(ignore_permissions=True)

        # Update the product_id column with the value of the name
        product_doc.product_id = product_doc.name
        product_doc.save(ignore_permissions=True)

        return {
            "StatusCode": 201,
            "Message": "Register Success",
            "Primarykey": str(product_doc.product_id),
        }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Upload  image of product in system
@frappe.whitelist(allow_guest=True)
def upload_image_product( product_id,image_file_name,video_file_name ):
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Upload Image of product
        for file_name in image_file_name:
            image_doc = frappe.get_doc(
                {
                    "doctype": "product_image",
                    "product_id": product_id,
                    "image_file_name": file_name,
                }
            )
            image_doc.insert(ignore_permissions=True)

            # Update the product_image_id column with the value of the name
            image_doc.product_image_id = image_doc.name
            image_doc.save(ignore_permissions=True)

        # Get Doctype at product_id
        product_doc = frappe.get_doc("products", product_id)

        # Update requirement status and link with supplier
        product_doc.product_video_file_name = video_file_name
        product_doc.save(ignore_permissions=True)

        return {"StatusCode": 201, "Message": "Upload and Update Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

###################################################### Market Action ########################################################

# Post new product in system
@frappe.whitelist(allow_guest=True)
def postnewproductv2(
    sub_id,
    product_name,
    image_file_name,
    video_file_name,
    product_category,
    product_description,
    product_brand,
    product_weight,
    product_license_number,
    product_country,
    product_size,
    product_amount,
    product_count,
    items,
    options ):
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Insert Product Option in product DB
        product_doc = frappe.get_doc(
            {
                "doctype": "products",
                "sub_id": sub_id,
                "product_name": product_name,
                "product_description": product_description,
                "product_count": product_count,
                "product_status": 1,
                "product_category": product_category,
                "product_brand": product_brand,
                "product_weight": product_weight,
                "product_county": product_country,
                "product_video_file_name": video_file_name,
                "product_license_number": product_license_number,
                "product_amount": product_amount,
                "product_size": product_size,
            }
        )
        product_doc.insert(ignore_permissions=True)

        # Update the product_id column with the value of the name
        product_doc.product_id = product_doc.name
        product_doc.save(ignore_permissions=True)
        
        # Upload Image of product
        for file_name in image_file_name:
            image_doc = frappe.get_doc(
                {
                    "doctype": "product_image",
                    "product_id": product_doc.name,
                    "image_file_name": file_name,
                }
            )
            image_doc.insert(ignore_permissions=True)

            # Update the product_image_id column with the value of the name
            image_doc.product_image_id = image_doc.name
            image_doc.save(ignore_permissions=True)

        # Start insert option of product
        column_name = []

        # Insert option price of this product
        # Insert at product ID
        plire_doc = frappe.get_doc(
            {
                "doctype": "product_options",
                "option_name": "Price",
                "product_id": product_doc.name,
            }
        )
        plire_doc.insert(ignore_permissions=True)
        plire_doc.option_id = plire_doc.name
        price_PK = plire_doc.name
        plire_doc.save(ignore_permissions=True)

        # Insert option Quantity (จำนวน) of this product
        quantity_doc = frappe.get_doc(
            {
                "doctype": "product_options",
                "option_name": "Quantity",
                "product_id": product_doc.name,
            }
        )
        quantity_doc.insert(ignore_permissions=True)
        quantity_doc.option_id = quantity_doc.name
        quantity_PK = quantity_doc.name
        quantity_doc.save(ignore_permissions=True)

        # Start insert option name
        for option in options:
            option_doc = frappe.get_doc(
                {
                    "doctype": "product_options",
                    "option_name": option["optionName"],
                    "product_id": product_doc.name,
                }
            )
            option_doc.insert(ignore_permissions=True)

            # Update the account_id column with the value of the name
            option_doc.option_id = option_doc.name
            option_doc.save(ignore_permissions=True)
            
            # Hold PK of option id in column_name
            column_name.append(option_doc.name)

        # Check column_name
        while len(column_name) < 5:
            # if column_name < 5 add 0 unless range of column_name = 5
            column_name.append("0")

        # Check column_name index not null if null skip
        if column_name[0] != "0":
            for index, item in enumerate(items):

                option_value_doc = frappe.get_doc(
                    {
                        "doctype": "product_option_values",
                        "option_id": column_name[0],
                        "value_name": item["optionGroupColumn1"],
                        "value_order": str(index + 1),
                    }
                )
                option_value_doc.insert(ignore_permissions=True)

                # Update the value_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)

        if column_name[1] != "0":
            for index, item in enumerate(items):

                option_value_doc = frappe.get_doc(
                    {
                        "doctype": "product_option_values",
                        "option_id": column_name[1],
                        "value_name": item["optionGroupColumn2"],
                        "value_order": str(index + 1),
                    }
                )
                option_value_doc.insert(ignore_permissions=True)

                # Update the value_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)

        if column_name[2] != "0":
            for index, item in enumerate(items):

                option_value_doc = frappe.get_doc(
                    {
                        "doctype": "product_option_values",
                        "option_id": column_name[2],
                        "value_name": item["optionGroupColumn3"],
                        "value_order": str(index + 1),
                    }
                )
                option_value_doc.insert(ignore_permissions=True)

                # Update the value_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)

        if column_name[3] != "0":
            for index, item in enumerate(items):

                option_value_doc = frappe.get_doc(
                    {
                        "doctype": "product_option_values",
                        "option_id": column_name[3],
                        "value_name": item["optionGroupColumn4"],
                        "value_order": str(index + 1),
                    }
                )
                option_value_doc.insert(ignore_permissions=True)

                # Update the value_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)

        if column_name[4] != "0":
            for index, item in enumerate(items):

                option_value_doc = frappe.get_doc(
                    {
                        "doctype": "product_option_values",
                        "option_id": column_name[4],
                        "value_name": item["optionGroupColumn5"],
                        "value_order": str(index + 1),
                    }
                )
                option_value_doc.insert(ignore_permissions=True)

                # Update the value_id column with the value of the name
                option_value_doc.value_id = option_value_doc.name
                option_value_doc.save(ignore_permissions=True)

        ## Map option_name price with price value and Insert Price of each option
        for index, item in enumerate(items):

            option_value_price_doc = frappe.get_doc(
                {
                    "doctype": "product_option_values",
                    "option_id": price_PK,
                    "value_name": item["optionGroupPrice"],
                    "value_order": str(index + 1),
                }
            )
            option_value_price_doc.insert(ignore_permissions=True)

            # Update the value_id column with the value of the name
            option_value_price_doc.value_id = option_value_price_doc.name
            option_value_price_doc.save(ignore_permissions=True)

        ## Map option_name quatity with quantity value and Insert Price of each option
        for index, item in enumerate(items):

            option_value_quantity_doc = frappe.get_doc(
                {
                    "doctype": "product_option_values",
                    "option_id": quantity_PK,
                    "value_name": item["optionGroupQuantity"],
                    "value_order": str(index + 1),
                }
            )
            option_value_quantity_doc.insert(ignore_permissions=True)

            # Update the value column with the value of the name
            option_value_quantity_doc.value_id = option_value_quantity_doc.name
            option_value_quantity_doc.save(ignore_permissions=True)

        write_log("Market {} add new product {} {} successfully" .format(sub_id, product_doc.name, product_name))
        return {"StatusCode": 201, "Message": "Register Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Market {} add new product {} {} failed with error {}" .format(sub_id, product_doc.name, product_name, str(e)))
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Update Product
@frappe.whitelist(allow_guest=True)
def active_not_sell_product(product_id):    
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Update product Status at product_id. status 4 is this product has not selling in system
        query = """UPDATE `tabproducts` SET product_status = 4 WHERE product_id = '%s'""" % (product_id)
        frappe.db.sql(query)

        # Commit the transaction
        frappe.db.commit()

        write_log("Market Not selling product {}".format(product_id))

        return {"statusCode": 200, "message": "Updata status Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("Market call api not selling order but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Active selling product
@frappe.whitelist(allow_guest=True)
def active_sell_product(product_id):
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Update product Status at product_id. status 2 is this product has back selling in system
        query = """UPDATE `tabproducts` SET product_status = 2 WHERE product_id = '%s'""" % (product_id)
        frappe.db.sql(query)

        # Commit the transaction
        frappe.db.commit()

        write_log("Market back to selling product {}".format(product_id))

        return {"statusCode": 200, "message": "Updata Back to selling Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("System call api confirm order but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

#######################################################################################################################

# save option of product in system
@frappe.whitelist(allow_guest=True)
def find_option_Detail(option_id):

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [option_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    try:
        # Find all option value of product_id
        optiondata = """ 
                        SELECT DISTINCT value_id, option_id, value_name
                        FROM `tabproduct_option_values` 
                        WHERE option_id = '%s' 
                    """ % (
            option_id
        )
        optionResults = frappe.db.sql(optiondata, as_dict=1)

        if len(optionResults) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Result": optionResults}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }


# @##########################################################################################
def find_option_Detail(options):
    option_results = []
    try:

        for option in options:
            optiondata = """ 
                            SELECT DISTINCT op.option_name, val.value_id, op.option_id, val.value_name
                            FROM `tabproduct_option_values` AS `val` 
                            INNER JOIN `tabproduct_options` AS `op`
                            ON val.option_id = op.option_id
                            WHERE val.option_id = '%s' 
                        """ % (
                option["option_id"]
            )
            optionResult = frappe.db.sql(optiondata, as_dict=1)
            option_results.extend(optionResult)

        # Group the data by option_name
        grouped_data = {
            key: list(group)
            for key, group in groupby(option_results, key=lambda x: x["option_name"])
        }

        return grouped_data

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }

def find_image_products(product_id):

    try:
        # Find all image filename of product_id
        query_image = """ 
                        SELECT product_id,image_file_name
                        FROM `tabproduct_image` 
                        WHERE product_id = '%s' 
                    """ % (product_id)
        image_list = frappe.db.sql(query_image, as_dict=1)

        if len(image_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Result": image_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500,"message": frappe.log_error(f"An error occurred: {str(e)}")}

# serach product detail in system
@frappe.whitelist(allow_guest=True)
def productdetailv2(product_id):

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    try:
        # Find product data in product_id
        data_product_query = """ SELECT * FROM `tabproducts` WHERE product_id = '%s' """ % (product_id)
        
        product_data_result = frappe.db.sql(data_product_query, as_dict=1)

        # Find all option_name in product_id
        All_option_query = """ 
                            SELECT option_id,option_name 
                            FROM `tabproduct_options` 
                            WHERE product_id = '%s' 
                            """ % (product_id)
        all_option = frappe.db.sql(All_option_query, as_dict=1)

        all_option_detail = find_option_Detail(all_option) # Send all_option to find option detial
        # return all option_name in this product

        all_product_image = find_image_products(product_id) # Find all image of this product
        
        # Find all product option_value in product_id
        Option_query = """
                    SELECT value_id,option_name, value_name, val.value_order FROM `tabproducts` AS pro 
                    INNER JOIN `tabproduct_options` AS op
                    ON pro.product_id = op.product_id
                    INNER JOIN `tabproduct_option_values` AS val
                    ON op.option_id = val.option_id
                    WHERE pro.product_id = "%s"
                    ORDER BY value_order
                """ % (product_id)
        productList = frappe.db.sql(Option_query, as_dict=1) # return all product option_value in this product

        # Sort the data based on value_order
        sorted_data = sorted(productList, key=lambda x: x["value_order"])

        # Group the sorted data by value_order
        grouped_data = {}
        for key, group in groupby(sorted_data, key=lambda x: x["value_order"]):
            grouped_data[f"Option{key}"] = list(group)

        
        if len(productList) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {
                "stausCode": "200",
                "message": "OK",
                "AllOption": all_option_detail,
                "data": product_data_result,
                "options": grouped_data,
                "images": all_product_image
            }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }
