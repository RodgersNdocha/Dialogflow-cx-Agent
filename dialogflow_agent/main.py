import pymysql


def handle_webhook(request):


   connection = pymysql.connect(unix_socket='/cloudsql/<project name>:<region>:<cloudsql instance name>',
                               user='<userid>',
                               password='<password>',
                               database='<db name>',
                               cursorclass=pymysql.cursors.DictCursor)


   req = request.get_json()
   tag = req["fulfillmentInfo"]["tag"]
   phone_number = str(int(req["sessionInfo"]["parameters"]["phone_number"]))


   if tag == "get_room_type":
       booking_date_year = str(int(req["sessionInfo"]["parameters"]["booking_date"]["year"]))
       booking_date_month = str(int(req["sessionInfo"]["parameters"]["booking_date"]["month"]))
       booking_date_day = str(int(req["sessionInfo"]["parameters"]["booking_date"]["day"]))
       booking_date = str(booking_date_year)+'-'+str(booking_date_month)+'-'+str(booking_date_day)
       with connection:
           with connection.cursor() as cursor:
               cursor.execute("SELECT A.room_type FROM room_type A left join (select room_type,count(*) as no_of_room_booked from booking where booking_date ='%s' group by room_type) B on A.room_type=B.room_type where COALESCE(num_of_rooms-no_of_room_booked,num_of_rooms) >0;" % booking_date)
               result = cursor.fetchall()
               result = ", ".join([str(row["room_type"]) for row in result])
       if result== "":
           msg="Sorry! No room is available for the booking date."
       else:
           msg= "Select the preferred room type. Below are the available Room types on the date {} \n {}".format(booking_date,result)
       res = {"fulfillment_response": {"messages": [{"text": {"text": [msg]}}]}}
       return res
   elif tag == "confirm_booking":
       room_type = req["sessionInfo"]["parameters"]["room_type"]
       booking_date_year = str(int(req["sessionInfo"]["parameters"]["booking_date"]["year"]))
       booking_date_month = str(int(req["sessionInfo"]["parameters"]["booking_date"]["month"]))
       booking_date_day = str(int(req["sessionInfo"]["parameters"]["booking_date"]["day"]))
       booking_date = str(booking_date_year)+'-'+str(booking_date_month)+'-'+str(booking_date_day)
       with connection:
           with connection.cursor() as cursor:
               cursor.execute("SELECT A.room_type FROM room_type A left join (select room_type,count(*) as no_of_room_booked from booking where booking_date ='%s' group by room_type) B on A.room_type=B.room_type where COALESCE(num_of_rooms-no_of_room_booked,num_of_rooms) >0;" % booking_date)
               result = cursor.fetchall()
               result = ", ".join([str(row["room_type"]) for row in result])
               if room_type in result:
                   sql_insert_query = """insert into booking values (%s,%s,%s)"""
                   cursor.execute(sql_insert_query, (phone_number,booking_date,room_type,))
                   connection.commit()
                   return None
               else:
                   res = {"sessionInfo": {"parameters": {"room_type": None,},},}
                   return res
   elif tag == "cancel_booking":
       booking_date_year = str(int(req["sessionInfo"]["parameters"]["booking_date"]["year"]))
       booking_date_month = str(int(req["sessionInfo"]["parameters"]["booking_date"]["month"]))
       booking_date_day = str(int(req["sessionInfo"]["parameters"]["booking_date"]["day"]))
       booking_date = str(booking_date_year)+'-'+str(booking_date_month)+'-'+str(booking_date_day)
       with connection:
           with connection.cursor() as cursor:
               cursor.execute("Delete FROM booking where booking_date =%s and phone_number = %s;", (booking_date,phone_number,))
               connection.commit()
               return None
   elif tag == "get_booking":
       with connection:
           with connection.cursor() as cursor:
               cursor.execute("select booking_date,room_type FROM booking where phone_number = %s;", (phone_number,))
               result = cursor.fetchall()
               result = ", ".join([f'{row["booking_date"]} with room type {row["room_type"]}' for row in result])
               len_result = len(result)
               if len(result) > 0:
                 result = f"You have Confirmed bookings on {result}"
               else:
                 result = f"You do not have any bookings with this number"


       res = {"fulfillment_response": {"messages": [{"text": {"text": [result]}}]}}
       return res
   else:
       result = f"There are no fulfillment responses defined for {tag} tag"
       res = {"fulfillment_response": {"messages": [{"text": {"text": [result]}}]}}
       return res