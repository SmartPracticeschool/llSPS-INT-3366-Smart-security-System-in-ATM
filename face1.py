import cv2
import numpy as np
import datetime

#ObjectStorage
import ibm_boto3
from ibm_botocore.client import Config, ClientError

#CloudantDB
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
import requests

face_classifier=cv2.CascadeClassifier("C:\\Users\\Syed Mahmood Ali. M\\Desktop\\AMINA project\\haarcascade_frontalface_default.xml")
eye_classifier=cv2.CascadeClassifier("C:\\Users\\Syed Mahmood Ali. M\\Desktop\\AMINA project\\haarcascade_eye.xml")




# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud" 
COS_API_KEY_ID = "J-V7nsp2hJyNRmt8spfL27c0Jv4Uu3Zy2DOFSrGjFVJZ"
COS_AUTH_ENDPOINT = "https://iam.ng.bluemix.net/oidc/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/dfb27ae6d4a649158049c7f228acdc14:777a934a-008d-4cb6-91ba-9c63ea32ea4c::"

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

#Provide CloudantDB credentials such as username,password and url

client = Cloudant("627f1286-d7f9-4104-b64d-06362110375c-bluemix", "5eba7ae2322504927b5f23ba5b8ae42ecb0bafa67a094f37de9a2c26ceb90065", url="https://627f1286-d7f9-4104-b64d-06362110375c-bluemix:5eba7ae2322504927b5f23ba5b8ae42ecb0bafa67a094f37de9a2c26ceb90065@627f1286-d7f9-4104-b64d-06362110375c-bluemix.cloudantnosqldb.appdomain.cloud")
client.connect()

#Provide your database name

database_name = "omnious1"

my_database = client.create_database(database_name)

if my_database.exists():
   print(f"'{database_name}' successfully created.")



def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


#It will read the first frame/image of the video
video=cv2.VideoCapture(0)

while True:
    #capture the first frame
    check,frame=video.read()
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    

    #detect the faces from the video using detectMultiScale function
    faces=face_classifier.detectMultiScale(gray,1.3,5)
    eyes=eye_classifier.detectMultiScale(gray,1.3,5)

    print(faces)
    
    #drawing rectangle boundries for the detected face
    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (127,0,255), 2)
        cv2.imshow('Face detection', frame)
        picname=datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
        cv2.imwrite(picname+".jpg",frame)
        multi_part_upload("sam012", picname+".jpg", picname+".jpg")
        json_document={"link":COS_ENDPOINT+"/"+"sam012"+"/"+picname+".jpg"}
        new_document = my_database.create_document(json_document)
        # Check that the document exists in the database.
        if new_document.exists():
            print(f"Document successfully created.")
        r = requests.get('https://www.fast2sms.com/dev/bulk?authorization=OTP53mqkBGDEzCwbRdSKIj2FLpax4sflXWJyr67hu1HZA8UovNbj6QRPwZ7HEJonLWtmOCyG3zVB8Np1&sender_id=FSTSMS&message=someone at the door&language=english&route=p&numbers=8688367172')
        print(r.status_code)
 #drawing rectangle boundries for the detected eyes
    for(ex,ey,ew,eh) in eyes:
        cv2.rectangle(frame, (ex,ey), (ex+ew,ey+eh), (127,0,255), 2)
        cv2.imshow('Face detection', frame)

    #waitKey(1)- for every 1 millisecond new frame will be captured
    Key=cv2.waitKey(10)
    if Key==ord('q'):
        break
        #release the camera
        video.release()
        #destroy all windows
        cv2.destroyAllWindows()
    

        
