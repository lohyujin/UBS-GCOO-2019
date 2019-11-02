from flask import *
from flask_cors import CORS, cross_origin
import pandas as pd
import functions as f
import uuid
import pyotp
import telegram
import os
from freshdesk.api import API

desk = API('perkbank.freshdesk.com', 'YNOcpORgEi6pOBwUtd9', version=2)
bot = telegram.Bot(token='650493546:AAG2mqXZ17UQvu-9GvBW_WWO3Ud3hWbufeY')
totp = pyotp.TOTP("JBSWY3PCBHPK3PXP")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'check/'
CORS(app)

@app.route("/login", methods = ['POST'])
def login():
        username = request.json['data'][0]
        password = request.json['data'][1]
        if(username == 'GGCOO' and password == 'UBSGCOO21'):
                success = 'True'
                token = str(uuid.uuid4())
                output = [success, token]
                msg = totp.now()
                chat_id = bot.get_updates()[-1].message.chat_id
                bot.send_message(chat_id=chat_id, text=msg)
        else:
                output = 'False'
        return jsonify(output)

@app.route("/2FA", methods = ['POST'])
def authenticate():
        code = request.json['data']
        return(str(totp.verify(code, valid_window = 60)))

@app.route("/reason", methods = ['GET'])
def reason():
        reason = pd.read_csv('UAE_Code.csv')
        output = reason.values.tolist()
        return jsonify(output)

@app.route("/check", methods = ['POST'])
def check():
        text = ''
        info = request.form
        currency = info['currency']
        acc_name = info['acc_name']
        ben_acc_no = info['ben_acc_no']
        ben_name = info['ben_name']
        bic = info['bic']
        path = 'check/' + acc_name
        if not os.path.exists(path):
                os.mkdir(path)
        if('compulsory_att' in info):
                return str(False)
        file1 = request.files['file1']
        file1.save(os.path.join(path, file1.filename))
        if ('optional_att' not in info):
                file2 = request.files['file2']
                print(file2.filename)
                file2.save(os.path.join(path, file2.filename))   
        check = [currency, acc_name, ben_acc_no, ben_name, bic]
        if('ben_address' in info):
                ben_address = info['ben_address']
                check.append(ben_address)
        print(check)
        output = f.regulation(check)
        dw_array = f.retrieve_files('Dataware', acc_name)
        user_array = f.retrieve_files('check', acc_name)
        files = dw_array + user_array
        if (output == False):
                return str(output)
        else:
                title = acc_name + ' to ' + ben_name
                for i in info: 
                        if(i == 'optional_att'):
                                break
                        text += i + '&emsp;' + info[i] + '<br>'
                        
                print(text)
                ticket = desk.tickets.create_ticket(subject= title,
                                email='ubsgcooca1@gmail.com',
                                description=text,
                                attachments = files,
                                responder_id = '48002814720',
                                priority='2'
                                )
                ticket_id = ticket.id
                final = ['True',ticket_id]
                return jsonify(final)
        return str(0)


@app.route("/staff", methods = ['POST'])
def staff_login():
        username = request.json['data'][0]
        password = request.json['data'][1]
        if(username == 'CA1' and password == 'ubsgcooca1'):
                success = 'True'
                token = str(uuid.uuid4())
                output = [success, token]
                msg = totp.now()
                chat_id = bot.get_updates()[-1].message.chat_id
                bot.send_message(chat_id=chat_id, text=msg)
        else:
                output = 'False'
        return jsonify(output)   

@app.route("/status", methods = ['POST'])
def status_check():
        sid = int(request.json['data'])
        return(desk.tickets.get_ticket(sid).status)

@app.route("/id", methods = ['POST'])
def populate():
        ticket_id = int(request.json['data'])
        fields = desk.tickets.get_ticket(ticket_id).description
        fields = fields.strip('</div>')
        fields = fields.strip('\n')
        fields = ''.join(fields)
        fields = fields.split('<br>')
        output = {}
        fields[:] = (value for value in fields if value != '')
        for i in fields:
                clean = i.split('\u2003')
                print(clean[1])
                key = clean[0]
                value = clean[1]
                output[key] = value

        return jsonify(output)

@app.route("/update", methods=['POST'])
def update():
        info = request.form
        text = ''
        for i in info: 
                if(i == 'ticket_id'):
                        pass
                text += i + '&emsp;' + info[i] + '<br>'
        ticket_id = int(info['ticket_id'])
        desk.tickets.update_ticket(ticket_id,
                description=text)

        return str(True)

if __name__ == "__main__":
        app.run()