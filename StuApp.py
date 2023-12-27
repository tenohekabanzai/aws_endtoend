from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddStu.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.facebook.com')


@app.route("/addstu", methods=['POST'])
def AddStu():
    stu_id = request.form['stu_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    stu_image_file = request.files['stu_image_file']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if stu_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (stu_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        stu_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        stu_image_file_name_in_s3 = "stu-id-" + str(stu_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=stu_image_file_name_in_s3, Body=stu_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                stu_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStuOutput.html', name=stu_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
