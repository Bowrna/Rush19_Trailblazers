# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.views.decorators.csrf import csrf_exempt
import MySQLdb
from random import randint
import sys
import datetime
from dateutil.relativedelta import *
from django.http import (HttpResponse, JsonResponse, HttpResponseForbidden)

from django.shortcuts import render

# Create your views here.
db=MySQLdb.connect(user="root",passwd="42madmonkeys",db="Rush")

@csrf_exempt
def push_medicine_detail(request):
    try:
        json_array = json.loads(request.body)
        db = MySQLdb.connect(user="root", passwd="42madmonkeys", db="Rush")
        #medicine_detail = []
        #purchase_detail = []
        for received_json_data in json_array:
            medicine = []
            purchase = []
            count =randint(40, 500)
            expire_month=randint(3,8)
            drug_name = received_json_data["drug_name"]
            company_name = received_json_data["company_name"]
            dosage = received_json_data["dosage"]
            price = received_json_data["price"]

            medicine.append(drug_name.lower())
            medicine.append(company_name.lower())
            medicine.append(dosage.lower())
            sql1 = "INSERT INTO MedicineDetails(DRUG_NAME,COMPANY_NAME,DOSAGE) values (%s,%s,%s)";
            mycursor = db.cursor()
            mycursor.execute(sql1, medicine)
            db.commit()

            sql2 = "SELECT MEDICINE_ID from MedicineDetails where (COMPANY_NAME=(%s) AND DOSAGE=(%s))";
            del medicine[0]
            print(medicine)
            mycursor.execute(sql2,tuple(medicine))
            result = mycursor.fetchone()
            medicine_id = result[0]
            print("Result",result[0])


            procurred_date = datetime.datetime.now().strftime("%Y-%m-%d")
            expiry_date = datetime.datetime.now() + relativedelta(months=+expire_month)
            expiry_date = expiry_date.strftime("%Y-%m-%d")
            purchase.append(medicine_id)
            purchase.append(procurred_date)
            purchase.append(expiry_date)
            purchase.append(price)
            purchase.append(count)
            print(purchase)
            sql3 = "INSERT INTO PurchaseDetails(MEDICINE_ID,PROCURRED_DATE,EXPIRY_DATE,PRICE,COUNT) values (%s,%s,%s,%s,%s)";
            mycursor.execute(sql3, purchase)
            db.commit()

            print(purchase)
        db.close()
    except:
        print('Oops things went wrong', sys.exc_info()[0], sys.exc_info()[1], " occurred.")
    return JsonResponse(received_json_data)

@csrf_exempt
def timetoday(request):
    procurred_date = datetime.datetime.now().strftime("%Y-%m-%d")
    expiry_date = datetime.datetime.now() + relativedelta(months=+1)
    print(expiry_date.strftime("%Y-%m-%d"))
    return HttpResponse("Hello world")

@csrf_exempt
def bill_medicine_detail(request):
    try:
        json_array = json.loads(request.body)
        medicine_needed = len(json_array)
        result = []
        db = MySQLdb.connect(user="root", passwd="42madmonkeys", db="Rush")
        mycursor = db.cursor()
        for received_json_data in json_array:
            print(received_json_data)
            output = {}
            bill = []
            company_name = received_json_data["company_name"]
            dosage = received_json_data["dosage"]
            count = received_json_data["count"]
            bill.append(count)
            bill.append(company_name)
            bill.append(dosage)
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            print(bill)
            sql = "SELECT MedicineDetails.DRUG_NAME,MedicineDetails.COMPANY_NAME,MedicineDetails.DOSAGE," \
                  "PurchaseDetails.COUNT,PurchaseDetails.PRICE,PurchaseDetails.EXPIRY_DATE," \
                  "MedicineDetails.MEDICINE_ID FROM MedicineDetails " \
                  "INNER JOIN PurchaseDetails ON MedicineDetails.MEDICINE_ID=PurchaseDetails.MEDICINE_ID " \
                  "WHERE (PurchaseDetails.COUNT >= (%s) AND MedicineDetails.COMPANY_NAME=(%s) " \
                  "AND MedicineDetails.DOSAGE=(%s))"
            mycursor.execute(sql, bill)
            row = mycursor.fetchone()
            print(row)
            if row and (len(row) > 0):
                print "You have stock available here"
                print(row)
                output["drug_name"]=row[0]
                output["company_name"]=row[1]
                output["dosage"] = row[2]
                available_count = row[3]
                price = row[4]
                expiry_date = row[5]
                medicine_id = row[6]

                new_count = available_count - count
                update_count = []
                update_count.append(new_count)
                update_count.append(medicine_id)
                sql1 = "UPDATE PurchaseDetails set COUNT=(%s) WHERE MEDICINE_ID=(%s)"
                mycursor.execute(sql1,update_count)
                db.commit()
                output["count"] = count
                output["price_per_unit"] = price
                output["total_price"] = str(count*price)
                output["available"] = True
            else:
                output["available"] = False
            print (output)
            result.append(output)
            db.commit()
        db.close()

    except:
        print('Oops things went wrong', sys.exc_info()[0], sys.exc_info()[1],sys.exc_info()[2],  "occurred.")
    return JsonResponse(result,safe=False)


