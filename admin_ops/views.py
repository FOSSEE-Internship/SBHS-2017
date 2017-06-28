# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pi_server import sbhs, settings
from pi_server.tables.models import Booking, Experiment, Slot
import json, os, serial, datetime
# Create your views here.

    # try:
    #     mid = int(req.POST.get('mid'))
    # except Exception as e:
    #     return HttpResponse(json.dumps({"status_code":500,"message":"Invalid Mid."+str(e)}))

    # try:
    #     conn = boards[mid]["board"]
    # except Exception as e:
    #     return HttpResponse(json.dumps({"status_code":500,"message":"No device with such MID."+str(e)}))
    # try:
    #     if not conn.is_open():
    #         conn.open()
    # except Exception as e:
    #     return HttpResponse(json.dumps({"status_code":500,"message":"Could not connect to device."+str(e)}))
    # 
    # try:
    #     if conn.reset_board():
    #         return HttpResponse(json.dumps({"status_code":200,"message":"Reset Successful","temp":conn.getHeat()}))
    #     else : 
    #         return HttpResponse(json.dumps({"status_code":500,"message":"Couldn't reset the device")}))
    # except Exception as e:
    #     return HttpResponse(json.dumps({"status_code":500,"message":"Couldn't reset the board."+str(e)}))
@csrf_exempt
def reset_device(req):
    """Resets the device to fan = 100 and heat = 0
        Takes mid as paramter 
        Returns status_code = 200, data={temp:temp of the device} if succesful
                else 
                status_code = 500 , data={error:errorMessage}
    """ 
    mid=int(req.POST.get('mid'))
    usb_path=settings.MID_PORT_MAP.get(mid,None)

    if usb_path is None:
        retVal={"status_code":400,"message":"Invalid MID"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    #trying to connect to device

    # check if SBHS device is connected
    if not os.path.exists(usb_path):
        retVal={"status_code":500,"message":"Device Not connected to defined USB Port"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    try:
        board = sbhs.Sbhs()
        board.machine_id=mid
        board.boardcon= serial.Serial(port=usb_path, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2) #orignal stopbits = 1
        board.status = 1
        if board.reset_board():
            retVal={"status_code":200,"message":board.getTemp()}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
        else:
            retVal={"status_code":500,"message":"Could not set the parameters.Try again."}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
    except serial.serialutil.SerialException:
        retVal={"status_code":500,"message":"Could not connect to the device.Try again."}
        return HttpResponse(json.dumps(retVal),content_type='application/json') 

@csrf_exempt
def set_device_params(req):
    """Sets the device parameters as per the arguments sent
        Takes mid,fan,heat as paramter 
        Returns status_code = 200, data={temp:temp of the device} if succesful
                else 
                status_code = 500 , data={error:errorMessage}
    """ 
    mid=int(req.POST.get('mid'))
    fan=int(req.POST.get('fan'))
    heat=int(req.POST.get('heat'))
    usb_path=settings.MID_PORT_MAP.get(mid,None)

    if usb_path is None:
        retVal={"status_code":400,"message":"Invalid MID"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    #trying to connect to device

    # check if SBHS device is connected
    if not os.path.exists(usb_path):
        retVal={"status_code":500,"message":"Device Not connected to defined USB Port"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    try:
        board = sbhs.Sbhs()
        board.machine_id=mid
        board.boardcon= serial.Serial(port=usb_path, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2) #orignal stopbits = 1
        board.status = 1
        if board.setFan(fan) and board.setHeat(heat):
            retVal={"status_code":200,"message":board.getTemp()}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
        else:
            retVal={"status_code":500,"message":"Could not set the parameters.Try again."}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
    except serial.serialutil.SerialException:
        retVal={"status_code":500,"message":"Could not connect to the device.Try again."}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

@csrf_exempt
def get_device_temp(req):
    """Sets the device parameters as per the arguments sent
        Takes mid,fan,heat as paramter 
        Returns status_code = 200, data={temp:temp of the device} if succesful
                else 
                status_code = 500 , data={error:errorMessage}
    """ 
    mid=int(req.POST.get('mid'))
    usb_path=settings.MID_PORT_MAP.get(mid,None)

    if usb_path is None:
        retVal={"status_code":400,"message":"Invalid MID"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    #trying to connect to device

    # check if SBHS device is connected
    if not os.path.exists(usb_path):
        retVal={"status_code":500,"message":"Device Not connected to defined USB Port"}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

    try:
        board = sbhs.Sbhs()
        board.machine_id=mid
        board.boardcon= serial.Serial(port=usb_path, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2) #orignal stopbits = 1
        board.status = 1
        temp=board.getTemp()
        if temp!=0.0:
            retVal={"status_code":200,"message":temp}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
        else:
            retVal={"status_code":500,"message":"Could not set the parameters.Try again."}
            return HttpResponse(json.dumps(retVal),content_type='application/json')
    except serial.serialutil.SerialException:
        retVal={"status_code":500,"message":"Could not connect to the device.Try again."}
        return HttpResponse(json.dumps(retVal),content_type='application/json')

@csrf_exempt
def monitor_experiment(req):
    mid = req.POST.get("mid")
    now = datetime.datetime.now()
    current_slot_id = Slot.objects.filter(start_hour=now.hour,
                                            start_minute__lt=now.minute,
                                            end_minute__gt=now.minute)

    current_slot_id = -1 if not current_slot_id else current_slot_id[0].id

    try:
        current_booking = Booking.objects.get(slot_id=current_slot_id,
                                                    booking_date=datetime.date.today(),
                                                    account__board__mid=mid)
    except Exception as e:
        print str(e)
        return HttpResponse(json.dumps({"status_code":400, "message":"Invalid MID"}), content_type="application/json")

    try:
        current_booking_id, current_user = current_booking.id, current_booking.account.username

        logfile = Experiment.objects.filter(booking_id=current_booking_id).order_by('created_at').reverse()[0].log
    except:
        return HttpResponse(json.dumps({"status_code":417, "message": "Experiment hasn't started"}), content_type="application/json")

    try:
        # get last 10 lines from logs
        stdin,stdout = os.popen2("tail -n 10 "+logfile)
        stdin.close()
        logs = stdout.readlines(); stdout.close()
        screened_logs = []
        for line in logs:
            screened_line = " ".join(line.split()[:4]) + "\n"
            screened_logs.append(screened_line)

        logs = "".join(screened_logs)
    except Exception as e:
        return HttpResponse(json.dumps({"status_code":500, "message":str(e)}), content_type="application/json")

    data = {"user": current_user, "logs": logs}
    return HttpResponse(json.dumps({"status_code":200, "message":data}), content_type="application/json")
