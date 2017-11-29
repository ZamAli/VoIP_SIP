import sys
import pjsua as sipapi
LOG_LEVEL = 3
current_call = None
#Logging method
def log_level(level, str, len):
    print str
    pass
#Define a function to make SIP call via library
def makeSipCall(uri1): #to make call
    try:
        print "Making call to", uri1
        return acc.make_call(uri1, cb=CallEventCallback())
    except sipapi.Error, e:
        print "Exception: return None" + str(e)
        return None
# Callback class for receive the incoming calls/events from SIP server.
class SipAccountReceiveCall(sipapi.AccountCallback): #receive events from account
    sem = None
    def __init__(self, account=None):
        sipapi.AccountCallback.__init__(self, account)
        pass
    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200: #check the status code
                self.sem.release()
                pass
            pass
# Notification on incoming call
    def on_incoming_call(self, call):
        global current_call
        if current_call:
            call.answer(486, "Busy")
            return
            pass
        print "Incoming call from ", call.info().remote_uri
        print "Enter 1 to answer the call"
        current_call = call
        call_cb = CallEventCallback(current_call)
        current_call.set_callback(call_cb)
# for ringing
        current_call.answer(180)
# callback class to receive events related call
class CallEventCallback(sipapi.CallCallback):
    def __init__(self, call=None):
        sipapi.CallCallback.__init__(self, call)
        pass
# Method to handle when call state has changed
    def on_state(self):
        global current_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,

        print "(" + self.call.info().last_reason + ")"
        pass
# Method to handle when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == sipapi.MediaState.ACTIVE: # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            sipapi.Lib.instance().conf_connect(call_slot, 0)
            sipapi.Lib.instance().conf_connect(0, call_slot)
            pass
        else:
            print "Media is not active" #when connection is not established.
            pass
# Main Code execution
siplib = sipapi.Lib() # create a library instance
try:
# Init library with default config and some customized logging config.
    siplib.init(log_cfg=sipapi.LogConfig(level=LOG_LEVEL, callback=log_level))
#Configuring one Transport Object and setting it to listen at 5060
    tran_conf = sipapi.TransportConfig()
    tran_conf.port = 5060 # 5060 is default port for SIP
    tran_conf.bound_addr = "192.168.0.32" # IP address of SIP client
    transport = siplib.create_transport(sipapi.TransportType.UDP, sipapi.TransportConfig(0))
    print "\nListening on", transport.info().host, # prints out the port number on which it is listening
    print "port", transport.info().port, "\n"
    siplib.start() # Start the library
# Account class configuration to register with Registrar server. User and password information
    are provided which is used as part of header to REGISTER SIP message
    acc_conf = sipapi.AccountConfig(domain='192.168.0.30', username='2000',
    password='password', display='2000', registrar='sip:192.168.0.30', proxy='sip:192.168.0.30')
    acc_conf.id = "sip:2000"
    acc_conf.reg_uri = "sip:192.168.0.30"
# Creating account object
    acc = siplib.create_account(acc_conf)
    cb = SipAccountReceiveCall(acc)
    acc.set_callback(cb)
# If argument is specified then make call to the URI
    if len(sys.argv) > 1:
        lck = siplib.auto_lock()
        current_call = makeSipCall(sys.argv[1])
        print 'Current call is', current_call
        del lck
        pass
    SipUri_mine = "sip:" + transport.info().host + \
        ":" + str(transport.info().port)
# Menu loop
    while True:
        print "Current User SIP URI: ", SipUri_mine
        print "\nPress:\n1 to make call\n2 to answer\n3 to hangup\n4 to quit\n"
        input = sys.stdin.readline().rstrip("\r\n")
        if input == '1':
            if current_call:
                print "On another call" #executed when destination endpoint is busy continue
                continue
            print "Enter in this format sip:2000@192.168.0.30 ",
            input = sys.stdin.readline().rstrip("\r\n")
            if input == "":
                continue
            lck = siplib.auto_lock()
            current_call = makeSipCall(input)
            del lck
        elif input == '2':
            if not current_call:
                print "No call connected"
                continue
            current_call.answer(200)
        elif input == '3':
            if not current_call:
                print "No call connected"
                continue
            current_call.hangup()
        elif input == '4':
            break
        transport = None
        acc.delete()
        acc = None
        siplib.destroy()
        siplib = None
    except sipapi.Error, e:
        print "Exception: " + str(e)
        siplib.destroy()
        siplib = None
